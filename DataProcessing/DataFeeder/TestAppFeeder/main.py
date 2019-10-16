from DataFeeder.AgentManager import Partition

partitions = []

class PartitionTestWebApp:
    def __init__(self, id):
        self.partition = Partition(id)
        self.allApps = {}

    def updateCallback(self, newItems, oldItems):
        for i in newItems:
            self.allApps.setdefault(i, 0)
            self.allApps[i]=self.allApps[i]+1

    def update(self, ts):
        self.allApps = {}
        self.partition.update(ts, self.updateCallback)

        allAppsList = []
        for k,v in self.allApps.items():
            allAppsList.append((k,v))11




for i in range(6):
    partitions.append(PartitionTestWebApp(i))





