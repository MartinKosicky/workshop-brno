from DataFeeder.Agent import Agent
from .name_list import allNames
import random

class Partition:
    def __init__(self, id):
        self.agents = []
        self.first_update = True
        pass

    def add_agent(self):
        self.agents.append(Agent(f"{random.choice(allNames)}_{len(self.agents)}"))

    def update(self, ts, callbackFunc):
        if self.first_update:
            self.first_update = False
            for agent in self.agents:
                callbackFunc(agent.GetState(), [])
        else:
            for agent in self.agents:
                if agent.DecrementTime(ts):
                    created, deleted = agent.UpdateState()
                    callbackFunc(created, deleted)





