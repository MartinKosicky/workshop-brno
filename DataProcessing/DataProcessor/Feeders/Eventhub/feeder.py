from DataProcessor.Processors import make_manager
from DataFeeder.AgentManager import Feeder
import threading
from Hubs import EventHubProcessor

import argparse

def start_feeding(num_threads, connection_string):
    def make_hub():
        hub = EventHubProcessor(
            connection_string,
            "g1", False)
        return hub

    def runner():
        feeder = Feeder(1000, make_hub())
        feeder.run()
        pass

    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=runner)
        t.start()
        threads.append(t)

    import time
    time.sleep(3600)

