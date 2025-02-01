import platform

import pygame

SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 850, 800

PLAYER_START_LIVES = 3
PLAYER_SPEED = 600
PLAYER_UPGRADE_TIME = 7
SHOT_COOLDOWN = 0.3
PLAYER_STASIS_TIME = 1
PLAYER_COLORS = ((0, 179, 243), (242, 45, 2))

BONUS_ALIEN_TYPE = 4
BONUS_ALIEN_SPEED = 400
BOSS_ALIEN_TYPE = 5
HEAVY_ALIEN_TYPE = 7
ACOLYTE_ALIEN_TYPE = 6

ACOLYTE_ALIEN_HP = 12
BOSS_ALIEN_HP = 100
BOSS_SHIELD_UP_PRC = 60
BOSS_CALL_ACOLYTE_PRC = 75

ALIENS_REWARD = [0, 10, 20, 30, 100, 5, 15, 40, 10]
MUSIC_END_EVENT = pygame.event.custom_type()
KEY_COOLDOWN = 0.2

MINIONS_COUNT = 12
MINIONS_MAX_BOMBS = 2
MINIONS_SPAWN_COOLDOWN = 0.4
MINION_BASE_SHOT_COOLDOWN = 2
BOSS_RESPAWN_MINIONS_COOLDOWN = 10
BOSS_SPAWN_TIMELIMIT = 8
SWARM_ALIEN_ACCURATE_SHOT_COUNT = 3

PARTICLES_HIT_COUNT = 10
PARTICLES_KILL_COUNT = {
    "Alien": 12,
    "MinionAlien": 12,
    "BossAlien": 80,
    "BonusAlien": 25,
    "AcolyteAlien": 40
}

PARTICLES_HIT_SIZE = (2, 6)
PARTICLES_KILL_SIZE = {
    "MinionAlien": (2, 6),
    "Alien": (3, 7),
    "BonusAlien": (3, 8),
    "AcolyteAlien": (3, 10),
    "BossAlien": (3, 10),
}


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
                 acolyte: bool,
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
        self.acolyte = acolyte


class PlayerKeys:
    def __init__(self, left, right, shot):
        self.left = left
        self.right = right
        self.shot = shot


level = [
    None,
    LevelSettings(8, (2, 2, 1, 1), (30, 250), 3.0, 0.3, (0, 0, 1, 0, 1, 2, 0, 1), 0, 0, 50, False),
    LevelSettings(8, (3, 2, 2, 1, 1), (40, 350), 2.5, 0.3, (0, 1, 2, 0, 1, 2, 0, 1), 0, 0, 60, False),
    LevelSettings(8, (3, 3, 3, 2, 2, 1), (50, 360), 2.0, 0.3, (1, 0, 1, 2, 1, 2, 0, 1), 0, 0, 70, False),
    LevelSettings(8, (7, 3, 3, 2, 2, 1), (50, 360), 2.0, 0.3, (1, 0, 2, 1, 2, 1, 0, 2), 0, 0, 80, False),
    LevelSettings(8, (7, 3, 3, 2, 2, 2), (60, 360), 1.8, 0.3, (1, 1, 2, 1, 2, 1, 2, 1), 0, 0, 80, True),
    LevelSettings(5, (3, 3, 2, 2, 1, 1), (70, 380), 1.6, 0.3, (0, 1, 2, 1, 2, 0, 1, 2), 20, 4, 60, True),
    LevelSettings(5, (7, 3, 3, 2, 2, 2), (70, 400), 1.5, 0.3, (1, 1, 2, 2, 1, 1, 2, 1), 40, 5, 90, False),
]

PLAYER_KEYS = [
    None,
    PlayerKeys(
        left=pygame.K_a,
        right=pygame.K_d,
        shot=pygame.K_SPACE
    ),
    PlayerKeys(
        left=pygame.K_LEFT,
        right=pygame.K_RIGHT,
        shot=1073742055 if platform.system() == "Darwin" else pygame.K_RCTRL
    )
]
