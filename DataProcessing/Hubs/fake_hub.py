import hashlib
import threading
import time

from .hub import Hub

class FakeHub(Hub):

    class Partition:
        def __init__(self):
            self.msgs = []
            self.lock = threading.Lock()
            pass

        def send_messages(self,msgs ,partition_key):
            with self.lock:
                self.msgs.extend(msgs)

        def process_msgs(self, callback):
            msgs = []
            with self.lock:
                msgs = self.msgs
                self.msgs = []

            try:
                callback(msgs)
            except Exception:
                with self.lock:
                    self.msgs = msgs + self.msgs
                    raise



    def __init__(self, partitions):
        self.partitions = [FakeHub.Partition() for _ in range(partitions)]

    def send_messages(self, msgs, partition_key):
        m = hashlib.md5()
        m.update(partition_key.encode())
        b = int.from_bytes(m.digest(),'big', signed=False) % len(self.partitions)

        self.partitions[b].send_messages(msgs, partition_key)

    def process_partition(self, partition_id, callback):
        self.partitions[partition_id].process_msgs(callback)

    def start_procesing(self, partition_id, processor_manager):
        while True:
            self.partitions[partition_id].process_msgs(processor_manager.on_process)
            time.sleep(0.2)




