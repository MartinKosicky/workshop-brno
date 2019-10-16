import os

namesFile = os.path.join(os.path.abspath(os.path.dirname(__file__)), "names.txt")
allNames = []
with open(namesFile,"r") as fp:
    lines = fp.readlines()
    for l in lines:
        allNames.append(l.rstrip())