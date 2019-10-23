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
        self.apps = {} # type: typing.Dict[str, typing.Set[str]]
        self.timeout_helper = TimeoutHelper()
        self.games_installed = {} # type: typing.Dict[str, typing.Set[str]]
        self.games_uninstalled = {} # type: typing.Dict[str, typing.Set[str]]

        self.games_installed_prev_minute = [] # type: typing.List[typing.Tuple[str,int]]
        self.games_uninstalled_prev_minute = [] # type: typing.List[typing.Tuple[str,int]]
        self.games_installed_prev_minute_and_not_uninstalled = [] # type: typing.List[typing.Tuple[str,int]]
        self.games_installed_prev_minute_and_uninstalled = []  # type: typing.List[typing.Tuple[str,int]]
        self.top_games_prev_minute = []

        self.last_installed_swap_time = time.time()

        pass



    # this function returns a sorted list of tuples (from highest), where first item is name of game and second is number of installations
    def _get_top_games(self) -> typing.List[typing.Tuple[str,int]] :
        game_list = sorted([(name, len(agent_list)) for name,agent_list in self.apps.items()],key=lambda v: v[1], reverse=True)[:10]
        return game_list

    #this function returns the number of games
    def _get_game_count(self) -> int:
        sum = 0
        for k,v in self.apps.items():
            sum += len(v)
        return sum

    def _update_top_games(self):
        self.communicator.set_top_games(self._get_top_games(), self.partition_id)

    def _update_game_count(self):
        self.communicator.update_game_count(self._get_game_count(), self.partition_id )

    def _on_agent_installed(self, game_name, agent_id):
        self.games_installed.setdefault(game_name, set()).add(agent_id)

    def _on_agent_uninstalled(self, game_name, agent_id):
        self.games_uninstalled.setdefault(game_name, set()).add(agent_id)


    def _update_statistics(self, cur_time):
        if cur_time - self.last_installed_swap_time > 20:
            print(f"{self.partition_id} : Handling swap")
            key = lambda x:x[1]


            games_installed = set()
            games_uninstalled = set()
            for game_name, agent_list in self.games_installed.items():
                for agent_id in agent_list:
                    games_installed.add((game_name, agent_id))
            for game_name, agent_list in self.games_uninstalled.items():
                for agent_id in agent_list:
                    games_uninstalled.add((game_name, agent_id))


            games_installed_and_uninstalled = games_installed.intersection(games_uninstalled)
            games_installed_ant_not_uninstalled = games_installed.difference(games_uninstalled)

            def set_to_count_map(s):
                result_map = {}
                for game_name, agent_id in s:
                    if game_name not in result_map:
                        result_map[game_name] = 0
                    result_map[game_name] = result_map[game_name] + 1

                return sorted([(k,v) for k,v in result_map.items()], reverse=True, key=lambda x:x[1])[:10]


            self.games_installed_prev_minute = sorted([(k,len(v)) for k,v in self.games_installed.items()], key=key, reverse=True)[:10]
            self.games_uninstalled_prev_minute = sorted([(k, len(v)) for k, v in self.games_uninstalled.items()], key=key, reverse=True)[:10]
            self.games_installed_prev_minute_and_uninstalled = set_to_count_map(games_installed_and_uninstalled)
            self.games_installed_prev_minute_and_not_uninstalled = set_to_count_map(games_installed_ant_not_uninstalled)
            self.top_games_prev_minute = self._get_top_games()


            self.games_installed = {}
            self.games_uninstalled = {}
            self.last_installed_swap_time = cur_time

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
