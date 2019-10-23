from DataProcessor.communicator import Comunicator

class ProcessorManager:
    def __init__(self, hub, partition_id):
        self.processors = []
        self.hub = hub
        self.partition_id = partition_id
        self.msg_counters = {}

    def add_processor(self, p):
        self.processors.append(p)

    def on_process(self, msgs):

        for m in msgs:
            if "type" in m:
                self.msg_counters.setdefault(m["type"],0)
                self.msg_counters[m["type"]] = self.msg_counters[m["type"]] + 1

        for p in self.processors:
            p.process(msgs)

        #print("Processed messages {} ".format(self.msg_counters))


def make_manager(hub, partition_id, url):

    from .apps_processor import TopAppProcessor2

    communicator = Comunicator(url)
    pm = ProcessorManager(hub, partition_id)
    pm.add_processor(TopAppProcessor2(partition_id,communicator))
    return pm