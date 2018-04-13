import redis
import os
from time import time, sleep
from tempfile import mkstemp
import _thread

from lib.parser import Parser
from lib.config import Config
from lib.server import HttpServer


if __name__ == '__main__':

    # build configuration
    c = Config()

    # start http server
    s = HttpServer(c)
    _thread.start_new_thread(s.run, ())

    # initiate redis client
    r = redis.StrictRedis(**c.redis())

    metrics = {}

    parser = Parser(r, metrics, c)

    while True:
        parser.consume()

        # get temporary file
        fd, tmppath = mkstemp()

        with open(tmppath, "w") as tmp:
            for host in list(metrics):
                for id in list(metrics.get(host)):

                    # write only the fresh metrics
                    if metrics.get(host).get(id).get('updated') + c.metricttl() > time():
                        tmp.write('{}\n'.format(metrics.get(host).get(id).get('body')))

                    # remove old guys
                    else:
                        del metrics[host][id]

        os.rename(tmppath, c.metricfilename())

        sleep(c.pullevery())
