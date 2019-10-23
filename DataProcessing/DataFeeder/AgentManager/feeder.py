from .partition import Partition
from Hubs import Hub
import time

class Feeder:
    def __init__(self, numAgents, hub:Hub):
        self.hub = hub
        self.partition = Partition(0)
        for _ in range(numAgents):
            self.partition.add_agent()

    def _callback(self, msgs):
        p = {}
        for m in msgs:
            partition_key = m["partition_key"]
            if partition_key not in p:
                p[partition_key] = []
            p[partition_key].append(m)

        for k,v in p.items():
            self.hub.send_messages(v,k)

    def run(self):
        while True:
            self.partition.update(0.5, self._callback)
            time.sleep(0.5)
