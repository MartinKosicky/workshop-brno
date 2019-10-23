from azure.eventhub import EventHubClient
from azure.eventhub import EventPosition, EventData, EventHubError
import json
from .hub import Hub
import time
import threading
import traceback
import sys

class EventHubProcessor(Hub):
    def __init__(self, connection_string, consumer_group, disable_send):
        Hub.__init__(self)
        self.client = EventHubClient.from_connection_string(connection_string)
        self.consumer_group = consumer_group
        self.producer = self.client.create_producer()
        self.lock = threading.Lock()
        self.msgs_to_send = {}
        self.sender_thread = threading.Thread(target=self._msg_sender_thread)
        self.sender_thread.start()
        self.disable_send = disable_send
        self.total_send = 0


    def _do_send_forever(self, event_batch, partition_key):
        while True:
            try:
                self.total_send  = self.total_send + event_batch._count
                self.producer.send(event_batch, partition_key)
                print(f"Total sent events: {self.total_send}")
                break
            except EventHubError as ex:
                self.producer = self.client.create_producer()
            except Exception as ex:
                print(ex)
                time.sleep(0.2)
                pass

    def _add_msgs_to_queue(self, msgs, partition_key):
        is_repeat = False
        while True:
            if is_repeat:
                time.sleep(0.1)
            with self.lock:
                m = self.msgs_to_send.setdefault(partition_key, [])
                if len(m) > 2000:
                    is_repeat = True
                    continue
                m.extend(msgs)
                return




    def _msg_sender_thread(self):
        while True:
            time.sleep(0.25)
            msgs_to_send = {}
            with self.lock:
                msgs_to_send = self.msgs_to_send
                self.msgs_to_send = {}

            wasData = True
            while wasData:
                wasData = False
                for k in msgs_to_send:
                    v = msgs_to_send[k][:100]
                    if len(v) > 0:
                        msgs_to_send[k]=msgs_to_send[k][100:]
                        self._send_msg_batch(v, k)
                        wasData = True




    def _send_msg_batch(self, msgs,partition_key):
        if self.disable_send:
            return

        event_data_batch = self.producer.create_batch(max_size=10000, partition_key=partition_key)

        #print(f"Send messages {len(msgs)} to partition_key {partition_key}")

        for msg in msgs:
            while True:
                try:
                    # self.producer.send(EventData(json.dumps(msg)),partition_key=partition_key)
                    event_data_batch.try_add(EventData(json.dumps(msg)))
                    break
                except Exception as ex:
                    #print(ex)

                    self._do_send_forever(event_data_batch, partition_key)
                    event_data_batch = self.producer.create_batch(max_size=10000, partition_key=partition_key)
        self._do_send_forever(event_data_batch, partition_key)



    def send_messages(self, msgs, partition_key):
        self._add_msgs_to_queue(msgs,partition_key)



    def start_procesing(self, partition_id, processor_manager):
        consumer = self.client.create_consumer(consumer_group="g1", partition_id=f"{partition_id}",
                                               event_position=EventPosition("@latest"), prefetch=1000)


        eventhub_counter = 0
        while True:
            with consumer:
                while True:
                    try:
                        received = []
                        for _ in range(5):
                            recv = consumer.receive(max_batch_size=1000, timeout=0.5)
                            received.extend(recv)
                            if len(recv)<300:
                                break

                        if len(received) > 0:
                            eventhub_counter = eventhub_counter + len(received)

                            while True:
                                try:
                                    processor_manager.on_process([r.body_as_json() for r in received])
                                    break
                                except Exception as ex:
                                    traceback.print_exc(file=sys.stdout)
                                    print(ex)
                                    pass
                            print(f"{partition_id} : Processed totally {eventhub_counter} msgs")
                    except:
                        raise
                    finally:
                        pass





