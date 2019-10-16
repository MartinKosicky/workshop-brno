from DataFeeder.TestData import GetApps
import time
import random

class Agent:
    NUM_APPS = 50
    MAX_SECS = 10.0
    KEYFRAME_MAX_SECS = 20.0

    def _init_ts(self, kfAlso=True):
        self.ts = (float(random.randint(0, 100)) / 100.0) * Agent.MAX_SECS
        if kfAlso:
            self.kfTs = Agent.KEYFRAME_MAX_SECS



    def __init__(self, name):
        self.apps = GetApps(Agent.NUM_APPS)
        self._init_ts()
        self.name = name

    def GetState(self):
        return self.apps


    def UpdateState(self):
        newAppList = GetApps(Agent.NUM_APPS)

        newApps = set(newAppList).difference(self.apps)
        deletedApps = set(self.apps).difference(newAppList)

        self.apps = newAppList
        self._init_ts()
        if self.kfTs < 0.0:
            self._init_ts()   # send keyframe
            return self.GetState(), deletedApps
        else:
            self._init_ts(False)  # send delta only
            return newApps, deletedApps

    def DecrementTime(self, ts):
        self.ts -= ts
        self.kfTs -= ts
        return self.ts < 0.0 or self.kfTs < 0.0

