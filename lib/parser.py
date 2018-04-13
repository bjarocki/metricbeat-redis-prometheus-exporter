from hashlib import md5
import json
from time import time


class Common:
    def __init__(self):
        pass

    def module(self):
        return self.payload.get('metricset').get('module')

    def name(self):
        return self.payload.get('metricset').get('name')

    def metricbody(self):
        return self.payload.get(self.module()).get(self.name())

    def hostname(self):
        return self.payload.get('beat').get('hostname')

    def hash(self, metric, labels):
        return md5('_'.join([self.hostname(), metric, ','.join(labels)]).encode('utf-8')).hexdigest()

    def extract(self, payload, parents=[], inheritedlabels=[]):
        locallabels = []

        # list of payload keys that we want to treat as a labels
        catch = ['name', 'devicename', 'mount_point', 'device_name', 'type', 'path', 'state']

        skipkeys = [k for k in payload.keys() if k in catch]

        for k in skipkeys:
            if self.metricbody().get(k):
                locallabels.append('{}="{}"'.format(k, self.metricbody().get(k)))

        for key in payload:

            # skip key that we decide to treat as label
            if key in skipkeys:
                continue

            if isinstance(payload.get(key), dict):
                self.extract(payload.get(key), parents + [key], inheritedlabels + locallabels)

            # XXX skip string values
            elif isinstance(payload.get(key), str):
                continue

            else:
                yield '_'.join(parents + [key]), ','.join(self.labels + inheritedlabels + locallabels), payload.get(key), self.hash('_'.join(parents + [key]), self.labels + inheritedlabels + locallabels)


class Parser():
    def __init__(self, redis_client, metrics, config):
        self.redis_client = redis_client
        self.metrics = metrics
        self.config = config

    def consume(self):
        while True:
            payload = self.redis_client.lpop(self.config.redis_metricbeat_key())

            if not payload:
                break

            try:
                payload = json.loads(payload)
                # print json.dumps(payload)
                module = payload.get('metricset').get('module')
                name = payload.get('metricset').get('name')
            except:
                continue

            # we'll try to use parsewith when creating parser object
            parsewith = '{}{}'.format(module.title(), name.title())

            # try to create parser object from custom class based on the metric module/name
            try:
                parser = eval(parsewith)(payload)
            except:
                parser = CommonParser(payload)

            for (m, labels, value, hash) in parser.prometheus():
                if not self.metrics.get(parser.hostname()):
                    self.metrics[parser.hostname()] = {}

                self.metrics[parser.hostname()][hash] = {'body': '{}{{{}}} {}'.format(m, labels, value), 'updated': time()}


class ZookeeperMntr(Common):
    def __init__(self, payload):
        self.payload = payload
        self.labels = ['hostname="{}"'.format(self.hostname()), 'zk_instance="{}"'.format(self.payload.get('metricset').get('host'))]

    def prometheus(self):
        return self.extract(self.metricbody(), [self.module(), self.name()])


class CommonParser(Common):
    def __init__(self, payload):
        self.payload = payload
        self.labels = ['hostname="{}"'.format(self.hostname())]

    def prometheus(self):
        return self.extract(self.metricbody(), [self.module(), self.name()])
