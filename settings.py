
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 850, 800
PLAYER_START_LIVES = 3
ALIENS_REWARD = [0, 10, 20, 30]
PLAYER_SPEED = 600
SHOT_COOLDOWN = 0.3

PLAYER_STASIS_TIME = 1


class LevelSettings:
    def __init__(self,
                 alien_in_line: int,
                 alien_types: tuple,
                 swarm_spd: tuple,
                 swarm_cd: float,
                 player_cd: float,
                 swarm_shot_order: tuple,
                 swarm_down_spd: int,
                 ):
        self.alien_types = alien_types
        self.swarm_spd = swarm_spd
        self.alien_in_line = alien_in_line
        self.swarm_cd = swarm_cd
        self.player_cd = player_cd
        self.swarm_shot_order = swarm_shot_order
        self.swarm_down_spd = swarm_down_spd


level = [
    None,
    LevelSettings(8, (3, 2, 2, 1, 1), (30, 250), 3.0, 0.3, (0, 0, 1, 0, 1, 1, 0, 1), 60),
    LevelSettings(8, (3, 3, 2, 2, 1, 1), (40, 350), 2.5, 0.3, (0, 0, 1, 0, 1, 1, 0, 1), 80),
    LevelSettings(8, (3, 3, 3, 2, 2, 1), (50, 360), 2.0, 0.3, (1, 0, 1, 1, 1, 1, 0, 1), 90),
]
