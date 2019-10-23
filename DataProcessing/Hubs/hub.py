class Hub:
    def __init__(self):
        pass

    def send_messages(self, msgs, partition_key):
        raise NotImplementedError()

    def send_all_msgs(self, msgs):
        pk = {}
        for m in msgs:
            partition_key = m["partition_key"]
            pk.setdefault(partition_key,[]).append(m)

        for k,v in pk.items():
            self.send_messages(v,k)