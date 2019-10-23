from DataProcessor.communicator import Comunicator
import time
import typing
import itertools

class TimeoutHelper:
    def __init__(self):
        self.timeout_marks = {}
        self.timeout_time = 100.0
        self.timeout_check_interval = 1.0
        self.last_timeout_check = time.time()

    def touch_agent_game(self, agent_id, game_name, cur_time):
        self.timeout_marks[(agent_id, game_name)] = cur_time

    def remove_agent_game(self, agent_id, game_name):
        self.timeout_marks.pop((agent_id, game_name), None)

    def handle_timeouts(self, cur_time):
        if cur_time < self.last_timeout_check + self.timeout_check_interval:
            return []

        self.last_timeout_check = cur_time

        items_to_remove = []

        for (agent_id, game_name), touched_time in self.timeout_marks.items():
            cur_delta = (cur_time - touched_time)
            if cur_delta > self.timeout_time:
                items_to_remove.append((agent_id, game_name))
        return items_to_remove


class TopAppProcessor2:

    def __init__(self,partition_id, communicator:Comunicator):
        self.partition_id = partition_id
        self.communicator = communicator

        self.timeout_helper = TimeoutHelper()

        ######### SET THIS SOMEWHERE IN CODE
        self.apps = {}  # type: typing.Dict[str, typing.Set[str]]      # apps is a dictionary of [game_name,  list of agent_ids
        self.games_installed = {} # type: typing.Dict[str, typing.Set[str]]   # dictionary of [game_name,  list of agent_ids],  reset in _update_statistics
        self.games_uninstalled = {} # type: typing.Dict[str, typing.Set[str]]  # dictionary of [game_name,  list of agent_ids],  reset in _update_statistics
        #######################################################################

        ############### STATISTICS #####################################################
        self.games_installed_prev_minute = [] # type: typing.List[typing.Tuple[str,int]]
        self.games_uninstalled_prev_minute = [] # type: typing.List[typing.Tuple[str,int]]
        self.games_installed_prev_minute_and_not_uninstalled = [] # type: typing.List[typing.Tuple[str,int]]
        self.games_installed_prev_minute_and_uninstalled = []  # type: typing.List[typing.Tuple[str,int]]
        self.top_games_prev_minute = []

        self.last_installed_swap_time = time.time()

        pass

    #this function returns the number of games
    def _get_game_count(self) -> int:
        sum = 0
        for k,v in self.apps.items():
            sum += len(v)
        return sum

    def _update_game_count(self):
        self.communicator.update_game_count(self._get_game_count(), self.partition_id )

    def _on_agent_installed(self, game_name, agent_id):
        # TODO: Implement this
        pass

    def _on_agent_uninstalled(self, game_name, agent_id):
        # TODO: Implement this
        pass



    def _update_statistics(self, cur_time):
        if cur_time - self.last_installed_swap_time > 20:
            print(f"{self.partition_id} : Handling swap")
            self.last_installed_swap_time = cur_time


            # TODO Implement this
            # Hint: accumulate data during 20 secs,
            # Swap togames_installed_prev_minute, games_uninstalled_prev_minute, games_installed_prev_minute_and_uninstalled, games_installed_prev_minute_and_not_uninstalled

            # Try first
            # 1. self.top_games_prev_minute
            # 2. games_installed_prev_minute , games_uninstalled_prev_minute
            # 3. games_installed_prev_minute_and_uninstalled,  games_installed_prev_minute_and_not_uninstalled
            #      hint: use set(installed this round -> tuple(game_name, agent_id)).difference(uninstalled this round -> tuple(game_name, agent_id))
            #      hint: use set(installed this round -> tuple(game_name, agent_id)).intersection(uninstalled this round -> tuple(game_name, agent_id))



        self.communicator.set_top_installed_games(self.games_installed_prev_minute, self.partition_id)
        self.communicator.set_top_uninstalled_games(self.games_uninstalled_prev_minute, self.partition_id)
        self.communicator.set_top_installed_and_uninstalled(self.games_installed_prev_minute_and_uninstalled, self.partition_id)
        self.communicator.set_top_installed_but_not_uninstalled(self.games_installed_prev_minute_and_not_uninstalled, self.partition_id)
        self.communicator.set_top_games(self.top_games_prev_minute, self.partition_id)








    def _handle_timeouts(self, cur_time):

        items_to_remove = self.timeout_helper.handle_timeouts(cur_time)

        for agent_id, game_name in items_to_remove:
            self._remove_agent_from_game(game_name, agent_id)


    def _add_agent_to_game(self, game_name, agent_id, cur_time):
        if game_name not in self.apps:
            self.apps[game_name] = set()

        if agent_id not in self.apps[game_name]:
            self._on_agent_installed(game_name, agent_id)

        self.apps[game_name].add(agent_id)
        self.timeout_helper.touch_agent_game(agent_id, game_name, cur_time)

    def _remove_agent_from_game(self, game_name, agent_id):
        self.timeout_helper.remove_agent_game(agent_id, game_name)

        if game_name in self.apps:
            agent_list = self.apps[game_name]
            if agent_id in agent_list:
                self._on_agent_uninstalled(game_name, agent_id)
                agent_list.discard(agent_id)



    def process(self, msgs):
        cur_time = time.time()
        for msg in msgs:
            if ("type" in msg) and (msg["type"]=="GameInstalledByName"):
                agent_id = msg["agent_id"]
                game_name = msg["game_name"]

                self._add_agent_to_game(game_name, agent_id, cur_time)

            elif ("type" in msg) and (msg["type"]=="GameUninstalledByName"):
                agent_id = msg["agent_id"]
                game_name = msg["game_name"]

                self._remove_agent_from_game(game_name, agent_id)

        self._handle_timeouts(cur_time)
        self._update_game_count()
        self._update_statistics(cur_time)
