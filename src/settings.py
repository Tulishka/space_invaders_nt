import pygame

SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 850, 800

PLAYER_START_LIVES = 3
PLAYER_SPEED = 600
SHOT_COOLDOWN = 0.3
PLAYER_STASIS_TIME = 1

BONUS_ALIEN_TYPE = 4
BONUS_ALIEN_SPEED = 400
BOSS_ALIEN_TYPE = 5
ALIENS_REWARD = [0, 10, 20, 30, 100, 5]
MUSIC_END_EVENT = pygame.event.custom_type()
KEY_COOLDOWN = 0.5
MINIONS_COUNT = 15
MINIONS_MAX_BOMBS = 2
MINIONS_SPAWN_COOLDOWN = 0.6
BOSS_RESPAWN_MINIONS_COOLDOWN = 10


class LevelSettings:
    def __init__(self,
                 alien_in_line: int,
                 alien_types: tuple,
                 swarm_spd: tuple,
                 swarm_cd: float,
                 player_cd: float,
                 swarm_shot_order: tuple,
                 swarm_rot_amp: int,
                 swarm_rot_spd: int,
                 swarm_down_spd: int,
                 ):
        self.alien_types = alien_types
        self.swarm_spd = swarm_spd
        self.alien_in_line = alien_in_line
        self.swarm_cd = swarm_cd
        self.player_cd = player_cd
        self.swarm_shot_order = swarm_shot_order
        self.swarm_rot_amp = swarm_rot_amp
        self.swarm_rot_spd = swarm_rot_spd
        self.swarm_down_spd = swarm_down_spd


level = [
    None,
    LevelSettings(8, (3, 2, 2, 1, 1), (30, 250), 3.0, 0.3, (0, 0, 1, 0, 1, 1, 0, 1), 0, 0, 60),
    LevelSettings(8, (3, 3, 2, 2, 1, 1), (40, 350), 2.5, 0.3, (0, 0, 1, 0, 1, 1, 0, 1), 0, 0, 80),
    LevelSettings(8, (3, 3, 3, 2, 2, 1), (50, 360), 2.0, 0.3, (1, 0, 1, 1, 1, 1, 0, 1), 0, 0, 90),
    LevelSettings(8, (3, 3, 3, 2, 2, 2), (60, 380), 1.7, 0.3, (1, 0, 1, 0, 1, 1, 0, 1), 0, 0, 100),
    LevelSettings(4, (3, 3, 2, 2, 1, 1), (70, 400), 1.5, 0.3, (1, 0, 1, 0, 1, 1, 0, 1), 40, 5, 110),
]
