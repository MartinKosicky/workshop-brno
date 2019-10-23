from DataProcessor.Feeders.Eventhub.processors import start_processors
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--partition_count","-p",required=False, default=5, type=int)
    parser.add_argument("--consumer_group","-g",required=False, default="g1", type=str)
    parser.add_argument("--url", default="http://127.0.0.1:9999")
    parser.add_argument("--connection_string", required=True)
    parser.add_argument("--enable_send", required=False, default=False, action="store_true")
    args = parser.parse_args()

    start_processors(args.connection_string, args.partition_count, args.consumer_group, args.url, not args.enable_send)