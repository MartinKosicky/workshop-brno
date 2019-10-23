from DataFeeder.Agent import Agent
from DataFeeder.Agent import Agent2
from .name_list import allNames
import random
from typing import List

class Partition:
    def __init__(self, id):
        self.agents = [] # type: List[Agent2]
        self.first_update = True
        self.game_counter = 0
        pass

    def add_agent(self):
        #self.agents.append(Agent(f"{random.choice(allNames)}_{len(self.agents)}"))
        self.agents.append(Agent2(f"{random.choice(allNames)}_{len(self.agents)}"))

    def update(self, ts, callbackFunc):
        game_counter = 0
        for agent in self.agents:
            kf_data = agent.keyframe(ts)
            if kf_data is not None:
                callbackFunc(kf_data)
            else:
                callbackFunc(agent.update(ts))
            game_counter = game_counter = len(agent.apps)
        '''if self.first_update:
            self.first_update = False
            for agent in self.agents:
                callbackFunc(agent.GetState())
                self.game_counter = self.game_counter + agent.GameCount()
        else:
            for agent in self.agents:
                if agent.DecrementTime(ts):
                    prevGameCount = agent.GameCount()
                    self.game_counter -= prevGameCount
                    callbackFunc(agent.UpdateState())
                    self.game_counter += agent.GameCount()
        '''

        self.game_counter = game_counter
        print(f"Total game count: {self.game_counter}")





