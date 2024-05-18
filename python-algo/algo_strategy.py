import gamelib
import random
import math
import warnings
from sys import maxsize
import json


"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical 
  board states. Though, we recommended making a copy of the map to preserve 
  the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP, ENEMY_HEALTH
        WALL = config["unitInformation"][0]["shorthand"]
        SUPPORT = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        MP = 1
        SP = 0
        # This is a good place to do initial setup
        ENEMY_HEALTH = 30
        self.scored_on_locations = []

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)

        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        game_state.suppress_warnings(True)  # Comment or remove this line to enable warnings.
        self.enemy_health_check(game_state)
        self.start_strategy_1(game_state)
        self.adapt_strategy(game_state)  # Added the new strategy method
        game_state.submit_turn()

    def enemy_health_check(self, game_state):
        global ENEMY_HEALTH
        if game_state.enemy_health < ENEMY_HEALTH:
            ENEMY_HEALTH = game_state.enemy_health
            if game_state.number_affordable(SCOUT) > 5:
                game_state.attempt_spawn(SCOUT, [12, 1], 1000)

        
    def start_strategy_1(self, game_state):
        self.build_defences(game_state)
        if game_state.turn_number % 3 == 2:
            game_state.attempt_spawn(DEMOLISHER, [12, 1], 1000)
            
    
    def build_defences(self, game_state):
        first_layer_walls = [[5, 12], [8, 12], [11, 12], [14, 12], [17, 12], [20, 12], [22, 12]]
        
        first_layer_turrets_a = [[0, 13], [1, 13], [2, 13], [25, 13], [26, 13], [27, 13], [1, 12], [2, 12], [3, 12], [4, 12], [25, 12], [26, 12], 
                                 [2, 11], [3, 11], [4, 11], [5, 11], [6, 11], [7, 11], [8, 11], [9, 11], [10, 11], [11, 11], [12, 11], [13, 11], 
                                 [14, 11], [15, 11], [16, 11], [17, 11], [18, 11], [19, 11], [20, 11], [21, 11], [22, 11], [24, 11], [25, 11], 
                                 [24, 10], [23, 9]]
        
        first_layer_support = [[13, 3], [14, 3], [13, 2], [14, 2]]
        
        second_layer_support = [[15, 4], [14, 4], [13, 4], [12, 4], [15, 5], [14, 5], [13, 5], [12, 5], [14, 6], [13, 6], [14, 7], [13, 7]]
        
        if game_state.turn_number <= 100 :
            game_state.attempt_spawn(TURRET, first_layer_turrets_a)
            game_state.attempt_upgrade(first_layer_support)
            game_state.attempt_spawn(SUPPORT, first_layer_support)
            game_state.attempt_spawn(WALL, first_layer_walls)
            game_state.attempt_upgrade(second_layer_support)
            game_state.attempt_spawn(SUPPORT, second_layer_support)
       
        
    def strategy(self, game_state, turrets, main_walls, support):
        """
        Strategy for the game. Waits until theres enough rescources to build a lot of scouts.
        """
        
        game_state.attempt_upgrade(turrets)
        game_state.attempt_upgrade(main_walls)
        self.build_support(game_state, support)
        game_state.attempt_upgrade(support)
        
        extra_support = [[13+i, 2+i] for i in range(4)] + [[13+i, 1+i] for i in range(10)]
        game_state.attempt_spawn(SUPPORT, extra_support)
        game_state.attempt_upgrade(extra_support)
        
        if game_state.number_affordable(DEMOLISHER) > 5:
            game_state.attempt_spawn(DEMOLISHER, [14, 0], num = 5)
           
            
    def build_support(self, game_state, support):
        for location in support:
            game_state.attempt_spawn(SUPPORT, location)    


    def send_demolisher(self, game_state):
        scout_locations = [[13, 0], [14, 0]]
        game_state.attempt_spawn(DEMOLISHER, scout_locations)
        
        
    def is_left_heavy(self, game_state):
        left_unit_count = self.detect_enemy_unit(game_state, valid_x=[0, 1, 2, 3, 4, 5, 6, 7], valid_y=[14, 15, 16, 17])
        right_unit_count = self.detect_enemy_unit(game_state, valid_x=[20, 21, 22, 23, 24, 25, 26, 27], valid_y=[14, 15, 16, 17])
        return left_unit_count > right_unit_count

    def adapt_strategy(self, game_state):
        self.build_initial_defences(game_state)
        if self.is_enemy_building_supports(game_state):
            self.send_mobile_units(game_state)
        else:
            self.continue_building_supports(game_state)

    def build_initial_defences(self, game_state):
        initial_turrets = [[3, 12], [24, 12]]
        game_state.attempt_spawn(TURRET, initial_turrets)
        initial_supports = [[13, 3], [14, 3], [13, 2], [14, 2]]
        game_state.attempt_spawn(SUPPORT, initial_supports)
        game_state.attempt_upgrade(initial_supports)
        first_layer_walls = [[5, 12], [8, 12], [11, 12], [14, 12], [17, 12], [20, 12], [22, 12]]
        game_state.attempt_spawn(WALL, first_layer_walls)
    
    def continue_building_supports(self, game_state):
        additional_supports = [[15, 4], [14, 4], [13, 4], [12, 4], [15, 5], [14, 5], [13, 5], [12, 5], [14, 6], [13, 6], [14, 7], [13, 7]]
        game_state.attempt_spawn(SUPPORT, additional_supports)
        game_state.attempt_upgrade(additional_supports)

    def is_enemy_building_supports(self, game_state):
        support_count = self.detect_enemy_unit(game_state, unit_type=SUPPORT)
        return support_count > 5

    def send_mobile_units(self, game_state):
        if self.enemy_has_many_turrets(game_state):
            if game_state.number_affordable(DEMOLISHER) > 0:
                game_state.attempt_spawn(DEMOLISHER, [13, 0], 1000)
        else:
            if game_state.number_affordable(SCOUT) > 0: 
                game_state.attempt_spawn(SCOUT, [13, 0], 1000)  
          
    def enemy_has_many_turrets(self, game_state):
        turret_count = self.detect_enemy_unit(game_state, unit_type=TURRET)
        return turret_count > 30  # I guess we can adjust this threshold as needed
          
    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """

    def build_reactive_defense(self, game_state):
        """
        This function builds reactive defenses based on where the enemy scored on us from.
        We can track where the opponent scored by looking at events in action frames 
        as shown in the on_action_frame function
        """
        for location in self.scored_on_locations:
            # Build turret one space above so that it doesn't block our own edge spawn locations
            build_location = [location[0], location[1]+1]
            game_state.attempt_spawn(TURRET, build_location)

    def least_damage_spawn_location(self, game_state, location_options):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to 
        estimate the path's damage risk.
        """
        damages = []
        # Get the damage estimate each path will take
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            damage = 0
            for path_location in path:
                # Get number of enemy turrets that can attack each location and multiply by turret damage
                damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(TURRET, game_state.config).damage_i
            damages.append(damage)
        
        # Now just return the location that takes the least damage
        return location_options[damages.index(min(damages))]

    def detect_enemy_unit(self, game_state, unit_type=None, valid_x = None, valid_y = None):
        total_units = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
                        total_units += 1
        return total_units
        
    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called 
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Processing the action frames is complicated so we only suggest it if you have time and experience.
        Full doc on format of a game frame at in json-docs.html in the root of the Starterkit.
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly, 
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write("All locations: {}".format(self.scored_on_locations))


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
