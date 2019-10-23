import requests
import random

def test_partition(partition):
    r = requests.post("http://127.0.0.1:9999/set_data", json={
        "partition": f"{partition}",
        "name": "ff",
        "type": "max",
        "values": [
            {
                "key":f"{partition}_{i}",
                "value":random.randint(100,1000)
            } for i in range(10)
        ]
    })

    r.raise_for_status()
    print(r.json())
    return r.json()

def get_data(episode):
    r = requests.get(f"http://127.0.0.1:9999/get_data_episode/{episode}/ff")
    return r.json()

try:
    test_partition("a")
    test_partition("b")
    test_partition("c")
    e = test_partition("d")
    print(get_data(e))
except requests.HTTPError as ex:
    print(ex.strerror)




#requests.get("http://127.0.0.1:9999/top_applications/0")'''