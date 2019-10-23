from Hubs import FakeHub
from DataProcessor.Processors import make_manager
from DataFeeder.AgentManager import Feeder
import threading



def main(url):
    hub = FakeHub(2)

    def runner():
        feeder = Feeder(1000, hub)
        feeder.run()

    threads = []
    for _ in range(1):
        t = threading.Thread(target=runner)
        t.start()
        threads.append(t)

    def run_process_partition(partition_id):
        manager = make_manager(hub, partition_id, url)
        hub.start_procesing(partition_id, manager)

    def process_partition(partition_id):
        t = threading.Thread(target=run_process_partition, args=(partition_id,))
        t.start()

    process_partition(0)
    process_partition(1)

    import time
    time.sleep(3600)


if __name__ == "__main__":
    main("http://localhost:9999")
