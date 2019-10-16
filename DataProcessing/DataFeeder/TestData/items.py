import os
import random

dataFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.txt")

items = []

all_items = [[],[]]
totalNumber = 0.0
with open(dataFile, "r") as fp:
    lines = fp.readlines()
    for l in lines:

        parts = l.rstrip().split("\t")
        items.append((parts[0], float(parts[-1])))
        totalNumber = totalNumber + float(parts[-1])

for i in range(len(items)):
    all_items[0].append(items[i][0])
    all_items[1].append(items[i][1] )



def GetApps(count):
    return random.choices(
    population=all_items[0],
    weights=all_items[1],
    k=count)


