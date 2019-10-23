from DataFeeder.AgentManager import Partition

partitions = []

class PartitionTestWebApp:
    def __init__(self, id):
        self.partition = Partition(id)

        for i in range(100):
            self.partition.add_agent()

        self.allApps = {}
        self.allDeletedApps = {}

    def updateCallback(self, newItems, oldItems):
        for i in newItems:
            self.allApps.setdefault(i, 0)
            self.allDeletedApps.setdefault(i,0)
            self.allApps[i]=self.allApps[i]+1
            self.allDeletedApps[i]=self.allDeletedApps[i]+1

    def update(self, ts):
        self.allApps = {}
        self.allDeletedApps = {}
        self.partition.update(ts, self.updateCallback)

        print("----------------------------------")
        print(self.allApps)
        print(self.allDeletedApps)

        def get_key(item):
            return item[1]

        print(sorted([(k,v) for k,v in self.allApps.items()], key=get_key, reverse=True))





for i in range(6):
    partitions.append(PartitionTestWebApp(i))

while True:
    import time
    time.sleep(1.0)
    for p in partitions:
        p.update(0.2)







