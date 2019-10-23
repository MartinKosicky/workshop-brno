from DataProcessor.Feeders.Eventhub.feeder import start_feeding
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--connection_string", required=True)
    parser.add_argument("--threads","-t", required=False, default=1)

    args = parser.parse_args()
    print("connection_string = {}".format(args.connection_string))
    print("num threads = {}".format(args.threads))
    start_feeding(args.threads, args.connection_string)