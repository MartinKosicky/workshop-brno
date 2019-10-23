from DataFeeder.TestData import GetApps, GetRequiredAppCount, GetRandomApp, GetAppCountDelta, TestData
import time
import random
import uuid
from Messages import game_installed_by_name, game_uninstalled_by_name

testData = TestData()

class Agent2:
    def __init__(self, name):
        self.id = str(uuid.uuid4())
        self.apps = []
        self.name = name

        self.ts_max = 1.0
        self.ts_left = random.random() * self.ts_max

        self.kf_max = 10.0
        self.kf_left = random.random() * self.kf_max

    def keyframe(self, ts):
        self.kf_left -= ts
        if self.kf_left > 0:
            return None

        self.kf_left = self.kf_max
        return [game_installed_by_name(self.id, name) for name in self.apps]


    def update(self, ts):
        self.ts_left -= ts
        if self.ts_left > 0:
            return []
        self.ts_left = self.ts_max

        prev_apps = self.apps
        self.apps = testData.change_apps(self.apps)

        added_apps = list(set(self.apps).difference(prev_apps))
        removed_apps = list(set(prev_apps).difference(self.apps))

        out_msgs = [game_installed_by_name(self.id, name) for name in added_apps]
        out_msgs.extend([game_uninstalled_by_name(self.id, name) for name in removed_apps])
        return out_msgs








class Agent:
    NUM_APPS = 10
    MAX_SECS = 2.0
    KEYFRAME_MAX_SECS = 10.0

    def _init_ts(self, kfAlso=True):
        self.ts = (float(random.randint(0, 100)) / 100.0) * Agent.MAX_SECS
        if kfAlso:
            self.kfTs = Agent.KEYFRAME_MAX_SECS



    def __init__(self, name):
        self.id = str(uuid.uuid4())
        self.apps = GetApps(GetRequiredAppCount())
        self._init_ts()
        self.name = name

    def GameCount(self):
        return len(self.apps)



    def GetState(self):
        apps = self._make_installed([app[0] for app in self.apps])
        print(f"GetState {self.name} with size {len(apps)}")
        return apps

    def _make_installed(self, apps):
        return [game_installed(self.id, self.name, app) for app in apps]

    def _make_uninstalled(self, apps):
        return [game_uninstalled(self.id, self.name, app) for app in apps]

    def UpdateState(self):
        print(f"Updating agent {self.name}")

        def extract_name(game_list):
            return [kv[0] for kv in game_list]

        oldAppsList = list(self.apps)

        deltaCount = int(GetAppCountDelta())
        newAppCount = len(self.apps) + deltaCount
        if newAppCount < 0 :
            newAppCount = 0

        if newAppCount > len(self.apps):
            self.apps = self.apps + GetApps(newAppCount - len(self.apps))
        elif len(self.apps) > newAppCount:
            appsToRemove = sorted(self.apps, key=lambda v : v[1], reverse=True)[:newAppCount]
            self.apps = appsToRemove

        # mutation

        for i in range(len(self.apps)):
            minAvg = self.apps[i][1] / 4.0
            if random.random() < minAvg:
                self.apps[i] = GetRandomApp()


        newApps = set(extract_name(self.apps)).difference(extract_name(oldAppsList))
        deletedApps = set(extract_name(oldAppsList)).difference(extract_name(self.apps))

        if self.kfTs < 0.0:
            self._init_ts()   # send keyframe
            return self.GetState() + self._make_uninstalled(deletedApps)
        else:
            self._init_ts(False)  # send delta only
            return self._make_installed(newApps) + self._make_uninstalled(deletedApps)

    def DecrementTime(self, ts):
        self.ts -= ts
        self.kfTs -= ts
        return self.ts < 0.0 or self.kfTs < 0.0

