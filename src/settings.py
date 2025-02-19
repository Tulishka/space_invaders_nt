"""
Файл содержит константы и настройки игры
"""

import platform

import pygame

from src.core.display import DisplayManager

# Размер игровой области на экране (не разрешение)
# Другие значения приведут к изменению геймплея!
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 850, 800

SCENE_KEY_COOLDOWN = 0.2

MUSIC_END_EVENT = pygame.event.custom_type()

PLAYER_START_LIVES = 3
PLAYER_SPEED = 600
PLAYER_UPGRADE_TIME = 7
PLAYER_SHOT_COOLDOWN = 0.3
PLAYER_STASIS_TIME = 1
PLAYER_COLORS = ((0, 179, 243), (242, 45, 2))

BOSS_ALIEN_TYPE = 5
BOSS_ALIEN_HP = 100
BOSS_SHIELD_UP_PRC = 60
BOSS_CALL_ACOLYTE_PRC = 75
BOSS_RESPAWN_MINIONS_COOLDOWN = 10

MINIONS_COUNT = 12
MINIONS_MAX_BOMBS = 2
MINIONS_SPAWN_COOLDOWN = 0.4
MINION_BASE_SHOT_COOLDOWN = 2

ACOLYTE_ALIEN_TYPE = 6
ACOLYTE_ALIEN_HP = 12

HEAVY_ALIEN_TYPE = 7
BONUS_ALIEN_TYPE = 4
BONUS_ALIEN_SPEED = 400

ALIENS_REWARD = [0, 10, 20, 30, 100, 5, 15, 40, 10]
SWARM_ALIEN_ACCURATE_SHOT_COUNT = 3

# Настройки частиц (количество при попадании и убийстве)
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


class PlayerKeys:
    def __init__(self, left, right, shot):
        self.left = left
        self.right = right
        self.shot = shot


# Кнопки для управления игроками
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

# Настройки дисплея
display_manager = DisplayManager(SCREEN_SIZE)
