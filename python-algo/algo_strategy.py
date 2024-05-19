import gamelib
import random
import math
import warnings
from sys import maxsize
import json


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
        global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP, ENEMY_HEALTH, RUSH
        WALL = config["unitInformation"][0]["shorthand"]
        SUPPORT = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        MP = 1
        SP = 0
        ENEMY_HEALTH = 30
        RUSH = False
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
        
        self.start_strategy_1(game_state)
        
        game_state.submit_turn()
        
    
    def enemy_health_check_attack(self, game_state):
        global ENEMY_HEALTH
        if game_state.enemy_health < ENEMY_HEALTH:
            ENEMY_HEALTH = game_state.enemy_health
            if game_state.number_affordable(SCOUT) > 5:
                game_state.attempt_spawn(SCOUT, [11, 2], 1000)

        
    def start_strategy_1(self, game_state):
        self.enemy_health_check_attack(game_state)
        
        self.remove_edge(game_state)
        self.build_defences(game_state)
        
        if game_state.turn_number == 10:
            self.early_support(game_state)
        elif game_state.turn_number <= 10:
            self.before_10(game_state)
            
        if game_state.turn_number % 4 == 0 and game_state.turn_number > 10:
            if random.randint(1,4) in [1,2,3]:
                game_state.attempt_spawn(DEMOLISHER, [12, 1], 1000)
            else:
                game_state.attempt_spawn(SCOUT, [12, 1], 1000)
    
    def build_defences(self, game_state):
        # Only build support units at the specified locations
        support_locations = [
            [21, 10], [20, 9], [20, 10], [19, 9], [19, 8],
            [19, 10], [22, 11], [21, 11], [20, 11], [18, 7],
            [18, 8], [18, 9], [18, 11]
        ]
        
        # Build turrets and walls as per the previous strategy
        first_layer_turrets_a = [[1, 13], [2, 13], [3, 13], [22, 13], [23, 13], [24, 13], [27, 13], [2, 12], [5, 12], 
                                 [6, 12], [9, 12], [10, 12], [13, 12], [14, 12], [17, 12], [18, 12], [20, 12], 
                                 [21, 12], [26, 12], [5, 11], [9, 11], [13, 11], [17, 11], [20, 11]]
        
        first_layer_walls = [[6, 13], [10, 13], [13, 13], [17, 13], [21, 13]]
        
        second_layer_turrets = [[0, 13], [4, 13], [21, 13], [1, 12], [3, 12], [4, 12], [7, 12], [8, 12], [11, 12], [12, 12], 
                                [15, 12], [16, 12], [19, 12], [22, 12], [23, 12], [20, 11], [21, 11], [22, 11], [25, 11], [2, 11], 
                                [3, 11], [4, 11], [5, 11], [6, 11], 
                                [7, 11], [8, 11], [9, 11], [10, 11], [11, 11], [13, 11], [14, 11], [15, 11], [16, 11], [17, 11], 
                                [19, 11], [20, 10], [21, 10], [24, 10], [4, 10], [5, 10], [6, 10], [9, 10], [10, 10], [11, 10], 
                                [14, 10], [15, 10], [16, 10], [19, 10]]
        
        game_state.attempt_spawn(TURRET, first_layer_turrets_a)
  
        if game_state.turn_number > 7:
            game_state.attempt_spawn(TURRET, second_layer_turrets)
            game_state.attempt_spawn(WALL, first_layer_walls)
            
        game_state.attempt_upgrade(support_locations)
        game_state.attempt_spawn(SUPPORT, support_locations)
        game_state.attempt_upgrade(first_layer_walls)
    
    def before_10(self, game_state):
        spawn_location = [[11, 2], [16, 2], [12, 1], [15, 1], [13, 0], [14, 0]]
        
        other_spawn = [[0, 13], [27, 13], [1, 12], [26, 12], [2, 11], [25, 11], [3, 10], 
                       [24, 10], [4, 9], [23, 9], [5, 8], [22, 8], [6, 7], [21, 7], [7, 6], 
                       [20, 6], [8, 5], [19, 5], [9, 4], [18, 4], [10, 3], [17, 3]]
        
        all_spawn = [[11, 2], [16, 2], [12, 1], [15, 1], [13, 0], [14, 0], [0, 13], [27, 13], 
                     [1, 12], [26, 12], [2, 11], [25, 11], [3, 10], [24, 10], [4, 9], [23, 9], 
                     [5, 8], [22, 8], [6, 7], [21, 7], [7, 6], [20, 6], [8, 5], [19, 5], [9, 4], 
                     [18, 4], [10, 3], [17, 3]]
        
        best_location = self.least_damage_spawn_location(game_state, spawn_location)
        
        if game_state.turn_number == 3:
            game_state.attempt_spawn(SCOUT, best_location, 13)
        elif game_state.turn_number == 8:
            game_state.attempt_spawn(SCOUT, best_location, 15)
        
        
    def early_support(self, game_state):
        global RUSH
        score = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.unit_type == 1 and unit.player_index == 1:
                        score += 1
                        if unit.upgraded:
                            score += 1
        if score >= 6:
            RUSH = True
            return True

        return False
            
           
    def remove_edge(self, game_state):
        edges = [[27, 13], [26, 12], [25, 11], [24, 10]]
        
        for edge in edges:
            if game_state.contains_stationary_unit(edge):
                if game_state.game_map[edge][0].health <= 20:
                    game_state.attempt_remove(edge)
                    game_state.attempt_spawn(TURRET, edge)
          
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
