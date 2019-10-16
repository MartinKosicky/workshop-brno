import requests
import random

def test_partition(partition):
    r = requests.post("http://127.0.0.1:9999/set_top_applications", json={
        "partition": f"{partition}",
        "episode": 0,
        "applications": [
            {
                "name":f"{partition}_{i}",
                "count":random.randint(100,1000)
            } for i in range(10)
        ]
    })

    r.raise_for_status()

    r = requests.post("http://127.0.0.1:9999/set_least_applications", json={
        "partition": f"{partition}",
        "episode": 0,
        "applications": [
            {
                "name":f"{partition}_{i}",
                "count":random.randint(100,1000)
            } for i in range(10)
        ]
    })

    r.raise_for_status()

try:
    test_partition("a")
    test_partition("b")
    test_partition("c")
    test_partition("d")
except requests.HTTPError as ex:
    print(ex.strerror)




#requests.get("http://127.0.0.1:9999/top_applications/0")'''