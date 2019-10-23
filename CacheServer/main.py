from flask import Flask, send_from_directory
from flask import request, jsonify
from flask_cors import CORS
from sortedcontainers import SortedDict, SortedSet, SortedList
import threading
import jsonschema
app = Flask(__name__)
cors = CORS(app)

max_applications = {}

import time
start_time = time.time()
episode_length = 10
episodes = SortedDict()

def get_current_episode():
    cur_time = time.time()
    return int((cur_time - start_time)/episode_length)


class Episode:
    def __init__(self, index):
        self.data = {}
        self.index = index
        pass

    def _ensure_name(self, name):
        if name not in self.data:
            self.data[name] = {}
        return self.data[name]

    def _set_values_for_partition(self, dt, partition, values):
        if "partitions" not in dt:
            dt["partitions"] = {}
        dt["partitions"][partition] = values

    def set_data_generic(self, type, partition, name, values):
        dt = self._ensure_name(name)
        dt["type"] = type
        self._set_values_for_partition(dt, partition, values)


    def _get_aggregator(self, type):

        def key_extractor(v):
            return v[1]

        def min_aggregator(values):
            return sorted(values, key=key_extractor )[:10]

        def max_aggregator(values):
            return sorted(values, key=key_extractor, reverse=True)[:10]

        def sum_aggregator(values):
            return sum([v for _,v in values])


        if type=="min":
            return min_aggregator
        elif type=="max":
            return max_aggregator
        elif type=="sum":
            return sum_aggregator
        else:
            return None



    def aggregate_data_for_name(self, name):
        if name not in self.data:
            return None

        type = self.data[name]["type"]
        all_data = []

        for _,v in self.data[name]["partitions"].items():
            all_data.extend(v)

        aggr = self._get_aggregator(type)
        if aggr is None:
            return None
        return aggr(all_data)

class EpisodeManager:
    def __init__(self):
        def key_extractor(v):
            if isinstance(v, Episode):
                return v.index
            return v

        self.episode_lock = threading.Lock()
        self.episodes = SortedDict()

    def _get_current_episode(self)->Episode:
        ep = get_current_episode()
        if ep not in self.episodes:
            self.episodes[ep] = Episode(ep)

        while len(self.episodes) > 20:
            self.episodes.popitem(0)

        return self.episodes[ep]

    def _get_previous_episode(self, ep)->Episode:
        if ep is None:
            ep = get_current_episode() - 2

        if ep not in self.episodes:
            if len(self.episodes) == 0:
                return None
            return self.episodes.peekitem()[1]
        return self.episodes[ep]

    def set_data_generic(self, type, partition, name, values ):
        with self.episode_lock:
            ep = self._get_current_episode()
            ep.set_data_generic(type, partition, name, values)
            return ep.index

    def aggregate_data_for_name_in_time(self, name, last_episode=None):
        with self.episode_lock:
            if last_episode is None:
                last_episode = get_current_episode() - 2

            all_data = []
            max_items = 20
            for k in reversed(self.episodes):
                if k<=last_episode:
                    all_data.append([k,self.episodes[k].aggregate_data_for_name(name)])
                    if len(all_data) > max_items:
                        break
            return all_data[::-1]






    def aggregate_data_for_name(self, name, episode=None):
        with self.episode_lock:
            episode = self._get_previous_episode(episode)
            if episode is None:
                return None
            return episode.aggregate_data_for_name(name)


episode_manager = EpisodeManager()


@app.errorhandler(jsonschema.exceptions.ValidationError)
def handle_validation_error(error):
    response = jsonify(error.to_dict())
    response.status_code = 400
    return response

@app.route('/set_data', methods=["POST"])
def set_data_for_generic():
    schema = {
        "type":"object",
        "required":["partition","values","name"],
        "properties":{
            "partition":{"type":"string"},
            "name":{"type":"string"},
            "type":{"type":"string"},
            "values": {
                "type":"array",
                "maxItems": 10,
                "items": {
                    "type":"object",
                    "properties":{
                        "key":{"type":"string"},
                        "value":{"type":"integer","minimum": 0, }
                     },
                    "required":["key","value"]
                }
             }
        }
    }



    data = request.get_json()
    jsonschema.validate(data, schema=schema)



    start_time = time.time()

    new_episode = episode_manager.set_data_generic(
        data["type"],
        data["partition"], data["name"],
        [(value["key"], value["value"]) for value in data["values"]]
    )

    end_time = time.time()
    print(f"Setting data for {data['name']} took {end_time-start_time}s")
    return jsonify(new_episode)


@app.route('/get_data_episode/<episode>/<name>', methods=["GET"])
def get_data_for_generic_episode(episode, name ):
    result = episode_manager.aggregate_data_for_name(name, int(episode))
    if result is None:
        return jsonify([])
    return jsonify(result)

@app.route('/get_data/<name>', methods=["GET"])
def get_data_for_generic(name):
    result = episode_manager.aggregate_data_for_name(name)
    if result is None:
        return jsonify([])
    return jsonify(result)

@app.route('/get_data_timeline/<name>', methods=["GET"])
def get_data_timeline(name):
    result = episode_manager.aggregate_data_for_name_in_time(name)
    if result is None:
        return jsonify([])
    return jsonify(result)

@app.route('/web/<path:path>')
def send_web(path):
    return send_from_directory("web", path)



if __name__=="__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port","-p",default=9999, type=int)
    args = parser.parse_args()

    app.run(host="0.0.0.0",port=args.port, threaded=True)
    #episode_manager.set_data_generic("max","0","xx",[("k",10),("v",22)])
