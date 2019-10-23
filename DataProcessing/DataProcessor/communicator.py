import requests
import threading
import time
from multiprocessing.dummy import Pool

class Comunicator:
    def __init__(self, url):
        self.url = url
        self.condition = threading.Condition()
        self.request_list = {}
        self.thread = threading.Thread(target=self._do_thread, args=())
        self.thread.start()


    '''
    '''

    def _run_requests_in_paralel(self, val):
        try:
            path, params = val
            requests.post(path, json=params)
        except Exception as ex:
            print("Failed communicating to {} because {}".format(path, ex))

    def _do_thread(self):
        while True:
            time.sleep(0.05)
            requests_to_process = []
            with self.condition:
                while len(self.request_list) == 0:
                    self.condition.wait()
                for k,v in self.request_list.items():
                    requests_to_process.append(v[-1])
                self.request_list = {}

            print(f"doing request")
            start_time = time.time()
            with Pool(len(requests_to_process)) as pool:
                pool.map(self._run_requests_in_paralel, requests_to_process)
            end_time = time.time()
            print(f"done request in {end_time - start_time}s")


    def _add_request(self, name, path, params):
        with self.condition:
            self.request_list.setdefault(name, []).append((path,params))
            self.condition.notify()



    def set_least_games(self, least_games, partition_id):
        self._add_request("least",f"{self.url}/set_data", {
                "partition": f"{partition_id}",
                "name": "least_apps",
                "type": "min",
                "values": [
                    {
                        "key": f"{k}",
                        "value": v,
                    } for k, v in least_games
                ]
            })

    def set_top_games(self, top_games, partition_id):
        self._add_request("top",f"{self.url}/set_data", {
                "partition": f"{partition_id}",
                "name": "top_apps",
                "type": "max",
                "values": [
                    {
                        "key": f"{k}",
                        "value": v,
                    } for k, v in top_games
                ]
            })

    def set_top_installed_games(self, top_games, partition_id):
        self._add_request("top_installed",f"{self.url}/set_data", {
                "partition": f"{partition_id}",
                "name": "top_installed",
                "type": "max",
                "values": [
                    {
                        "key": f"{k}",
                        "value": v,
                    } for k, v in top_games
                ]
            })

    def set_top_uninstalled_games(self, top_games, partition_id):
        self._add_request("top_uninstalled",f"{self.url}/set_data", {
                "partition": f"{partition_id}",
                "name": "top_uninstalled",
                "type": "max",
                "values": [
                    {
                        "key": f"{k}",
                        "value": v,
                    } for k, v in top_games
                ]
            })

    def set_top_installed_but_not_uninstalled(self, top_games, partition_id):
        self._add_request("top_installed_not_uninstalled",f"{self.url}/set_data", {
                "partition": f"{partition_id}",
                "name": "top_installed_not_uninstalled",
                "type": "max",
                "values": [
                    {
                        "key": f"{k}",
                        "value": v,
                    } for k, v in top_games
                ]
            })

    def set_top_installed_and_uninstalled(self, top_games, partition_id):
        self._add_request("top_installed_and_uninstalled",f"{self.url}/set_data", {
                "partition": f"{partition_id}",
                "name": "top_installed_and_uninstalled",
                "type": "max",
                "values": [
                    {
                        "key": f"{k}",
                        "value": v,
                    } for k, v in top_games
                ]
            })


    def update_game_count(self, game_count, partition_id):
        self._add_request("counts",f"{self.url}/set_data", {
                "partition": f"{partition_id}",
                "name": "apps_count",
                "type": "sum",
                "values": [
                    {
                        "key": f"dummy",
                        "value": game_count,
                    }
                ]
            })

