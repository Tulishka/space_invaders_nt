import pygame
from pygame.sprite import Sprite

from projectile import Bullet

import settings
from scene_manager import SceneManager
from sound import sounds


class PlayerKeys:
    def __init__(self, left, right, shot):
        self.left = left
        self.right = right
        self.shot = shot


class Player(Sprite):
    PLAYER_KEYS = [
        None,
        PlayerKeys(
            left=pygame.K_a,
            right=pygame.K_d,
            shot=pygame.K_SPACE,
        ),
        PlayerKeys(
            left=pygame.K_LEFT,
            right=pygame.K_RIGHT,
            shot=pygame.K_RCTRL,
        ),
    ]

    def __init__(self, num: int, sprite_group, scene_manager: SceneManager, bullets_group, start_x: int):
        super().__init__(sprite_group)
        self.bullets_group = bullets_group
        self.num = num
        self.image = pygame.image.load(f'./img/player{self.num}.png')
        self.kill_image = pygame.image.load(f'./img/player{self.num}k.png')
        self.rect = self.image.get_rect(
            center=(
                start_x,
                settings.SCREEN_HEIGHT - self.image.get_height()
            )
        )
        self.time = 0
        self.spd = settings.PLAYER_SPEED
        self.scene_manager = scene_manager
        self.keys = self.PLAYER_KEYS[self.num]
        self.alt_keys = self.PLAYER_KEYS[self.num]
        self.shot_cooldown = 1
        self.dead = False

        self.sound_shot = sounds[f"player_shot{self.num}"]


    def shot(self):
        self.shot_cooldown = settings.SHOT_COOLDOWN
        Bullet(self.rect.midtop, self.bullets_group, self)
        self.sound_shot.play()

    def update(self, dt):
        self.time += dt
        self.shot_cooldown -= dt

        if self.dead:
            return

        if self.shot_cooldown < 0:
            self.shot_cooldown = 0
        keys = pygame.key.get_pressed()
        if (keys[self.keys.left] or keys[self.alt_keys.left]) and self.rect.left > 0:
            self.rect.x -= self.spd * dt
        if (keys[self.keys.right] or keys[self.alt_keys.right]) and self.rect.right < settings.SCREEN_WIDTH:
            self.rect.x += self.spd * dt
        if (keys[self.keys.shot] or keys[self.alt_keys.shot]) and self.shot_cooldown == 0:
            self.shot()

    def die(self):
        if not self.dead:
            self.image = self.kill_image
            self.dead = True
