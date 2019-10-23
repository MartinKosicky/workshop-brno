import os
import random
import math
import numpy
import time

dataFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "default_data.txt")

items = []

all_items = [[],[]]
minValue = None

def CDF(x, mean, variance):
    return 0.5 * (1 + math.erf((x-mean)/(variance*math.sqrt(2.0))))

def MakeProbability(mean, variance):
    return CDF(numpy.random.normal(mean,variance), mean, variance)

with open(dataFile, "r") as fp:
    lines = fp.readlines()

    for l in lines:

        parts = l.rstrip().split("\t")


        v = MakeProbability(0,20)
        items.append((parts[0], v*v*v*v*v*v))

def key_getter(v):
    return v[1]

items = sorted(items, reverse=True, key=key_getter)
for i in range(len(items)):

    all_items[0].append((items[i][0], items[i][1]))
    all_items[1].append(items[i][1])






#exit(0)

game_count_mean = 0
game_mean_variance = 0
first_load = False
last_config_load = time.time()
max_config_load = 2

def LoadConfig():
    global first_load
    global last_config_load
    global game_mean_variance
    global game_count_mean

    cur_time = time.time()
    if not first_load or (cur_time - last_config_load)>max_config_load:
        first_load = True
        last_config_load = cur_time

        config_fname = os.path.join(os.path.dirname(__file__),"config.txt")
        with open(config_fname,"r") as fp:
            lines = fp.readlines()
            for l in lines:
                l = l.rstrip()
                parts = l.split(" ")
                if parts[0]=="game_count_mean":
                    game_count_mean = float(parts[1])
                elif parts[0]=="game_count_variance":
                    game_mean_variance = float(parts[1])



def GetRandomApp():
    LoadConfig()

    return random.choices(
    population=all_items[0],
    weights=all_items[1],
    k=1)[0]

def GetRequiredAppCount():
    LoadConfig()

    app_count = int(numpy.random.normal(game_count_mean,game_mean_variance))
    if app_count < 0:
        app_count = 0

    return app_count

def GetAppCountDelta():
    LoadConfig()

    return numpy.random.normal(0, 1.5)

def GetApps(count):

    LoadConfig()

    return random.choices(
    population=all_items[0],
    weights=all_items[1],
    k=count)

if __name__ == "__main__":
    print(sorted(all_items[1], reverse=True))
    uniqueValues = set()

    for i in range(10):
        apps = GetApps(10)
        for a in apps:
            uniqueValues.add(a)
        print(apps)

    print(f"Unique values = {uniqueValues}")
    print(f"Unique values length = {len(uniqueValues)}")

