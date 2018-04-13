import os
import sys


class Config:
    def __init__(self):
        pass

    def redisdb(self):
        return os.environ.get('REDIS_DB') or 0

    def redishost(self):
        return os.environ.get('REDIS_HOST') or sys.exit('Missing REDIS_HOST variable')

    def redisport(self):
        return os.environ.get('REDIS_PORT') or 6379

    def httpport(self):
        return os.environ.get('HTTP_PORT') or 8080

    def metricfilename(self):
        return os.environ.get('METRIC_FILE') or '/tmp/metrics'

    def metricttl(self):
        return 600

    def pullevery(self):
        return 2

    def redis_metricbeat_key(self):
        return os.environ.get('REDIS_METRICBEAT_KEY') or 'metricbeat'

    def redis(self):
        return {'host': self.redishost(), 'port': self.redisport(), 'db': self.redisdb()}
