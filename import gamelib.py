import gamelib
import random
import math
import warnings
from sys import maxsize
import json

class AlgoStrategy(gamelib.AlgoCore):
    def init(self):
        super().init()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

    def on_game_start(self, config):
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP
        WALL = config["unitInformation"][0]["shorthand"]
        SUPPORT = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        MP = 1
        SP = 0
        self.scored_on_locations = [[8, 5]]

    def on_turn(self, turn_state):
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.
        self.starter_strategy(game_state)
        game_state.submit_turn()

    def starter_strategy(self, game_state):
        #self.build_reactive_defense(game_state)
        self.build_initial_defences(game_state)
        if game_state.turn_number % 3 == 2:
            game_state.attempt_spawn(DEMOLISHER, [4, 9], 1000)
        if game_state.turn_number % 2 != 0:
            last_scored_location = self.scored_on_locations[-1]
            
    def build_initial_defences(self, game_state):
        tier1_destructors_points = [[27, 13], [26, 12], [25, 12],[0, 13], [1, 12], [2, 12], [25, 11],[5, 11], 
                                    [3,11], [23,11], [24, 11],[6, 10],[7, 9],[22, 11], [8, 8], [9, 7],  [13, 11], 
                                    [21, 10],[10, 6], [20, 9], [11, 5], [19, 8], [11, 11],[18, 7], [12, 4], [17, 6], 
                                    [14, 11], [16, 5],[15, 4],[13,4],[14,4], [5, 10],[22,10],[6,10], [21,10], [7,10],[20,10]]
        tier2_destructors_points = [[13,10],[14,10],[13,9],[14,9],[13,8],[14,8]]
        tier1_upgrades_points =   [[27, 13], [26, 12], [25, 12],[0, 13], [1, 12], [2, 12], [25, 11],[5, 11], [3,11], [23,11], [24, 11],[6, 10],[7, 9],[22, 11], [8, 8], [9, 7],  [13, 11], [21, 10],[10, 6], [20, 9], [11, 5], [19, 8], [11, 11],[18, 7], [12, 4], [17, 6], [14, 11], [16, 5],[15, 4],[13,4],[14,4], [5, 10],[22,10],[6,10], [21,10], [7,10],[20,10]]
        support_points = [[2,11],[3,10]]
        secondary_support_points = [[1, 13], [26,13],[3, 12],[24,12]]
        if game_state.turn_number == 1 :
            game_state.attempt_spawn(SUPPORT, support_points)
            game_state.attempt_upgrade(support_points)
        if game_state.turn_number <= 23:
            if game_state.turn_number % 3 == 2:
                game_state.attempt_spawn(SUPPORT, support_points)
            game_state.attempt_spawn(TURRET, tier1_destructors_points)
            game_state.attempt_spawn(WALL, secondary_support_points)
            game_state.attempt_upgrade(support_points)
            game_state.attempt_upgrade(secondary_support_points)
        if game_state.turn_number > 23:
            game_state.attempt_upgrade(support_points)
            game_state.attempt_spawn(TURRET, tier2_destructors_points)
            game_state.attempt_spawn(TURRET, tier1_destructors_points)
        game_state.attempt_spawn(SUPPORT, support_points)
        game_state.attempt_upgrade(support_points)
        game_state.attempt_spawn(TURRET, tier1_destructors_points)
        game_state.attempt_upgrade(support_points)
        #game_state.attempt_upgrade(secondary_support_points)
        #game_state.attempt_spawn(SUPPORT, secondary_support_points)
        #game_state.attempt_upgrade(secondary_support_points)
        game_state.attempt_upgrade(tier1_upgrades_points)
        game_state.attempt_spawn(TURRET, tier1_upgrades_points)
        game_state.attempt_upgrade(support_points)
        game_state.attempt_spawn(SUPPORT, support_points)
        game_state.attempt_upgrade(support_points)
        game_state.attempt_spawn(TURRET, tier2_destructors_points)

    def is_left_heavy(self, game_state):
        left_unit_count = self.detect_enemy_unit(game_state, valid_x=[0, 1, 2, 3], valid_y=[14, 15, 16, 17])
        right_unit_count = self.detect_enemy_unit(game_state, valid_x=[24, 25, 26, 27], valid_y=[14, 15, 16, 17])
        return left_unit_count > right_unit_count

    def detect_enemy_unit(self, game_state, unit_type=None, valid_x = None, valid_y = None):
        total_units = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
                        total_units += 1
        return total_units

    def on_action_frame(self, turn_string):
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write("All locations: {}".format(self.scored_on_locations))

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()