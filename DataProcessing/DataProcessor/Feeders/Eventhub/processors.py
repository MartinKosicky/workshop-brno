from Hubs import EventHubProcessor
from DataProcessor.Processors import make_manager
from DataFeeder.AgentManager import Feeder
import threading


def start_processors(connection_string, partition_count, consumer_group,  url, disable_send):
    def make_hub(connection_string, consumer_group, disable_send):
        hub = EventHubProcessor(
            connection_string,
            consumer_group,
            disable_send)
        return hub

    def run_process_partition(connection_string,consumer_group, partition_id, url, disable_send):
        hub = make_hub(connection_string, consumer_group,disable_send)
        manager = make_manager(hub, partition_id, url)
        hub.start_procesing(partition_id, manager)

    def process_partition(partition_id, url, connection_string,consumer_group, disable_send):
        t = threading.Thread(target=run_process_partition, args=(connection_string, consumer_group, partition_id,url,disable_send, ))
        t.start()


    for i in range(partition_count):
        process_partition(i,url, connection_string, consumer_group, disable_send)