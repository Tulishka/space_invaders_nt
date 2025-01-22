import random

import pygame
from pygame.sprite import Sprite

import settings
from projectile import Bomb
from sound import play_sound


class Alien(Sprite):
    ALIEN_DEAD_TIME = 0.25

    def __init__(self, aliens_group, pos, type_, column, bombs_group):
        super().__init__(aliens_group)
        self.aliens_group = aliens_group
        self.type = type_
        self.images = [
            pygame.image.load(f'./img/enemy{self.type}.png'),
            pygame.image.load(f'./img/enemy{self.type}b.png'),
        ]
        self.kill_image = pygame.image.load(f'./img/enemy{self.type}k.png')

        self.image = self.images[0]
        self.rect = self.image.get_rect(center=pos)
        self.time = random.random()
        self.kill_time = 0
        self.column = column
        self.bombs_group = bombs_group
        self.x, self.y = pos
        self.animation_spd = 2

    def update(self, dt) -> None:
        self.time += dt
        if self.kill_time > 0:
            if self.time > self.kill_time:
                self.kill()
        else:
            self.image = self.images[int(self.time * self.animation_spd + self.type * 0.5) % len(self.images)]

    def shot(self, spd_scale=1):
        Bomb(self.rect.midbottom, self.bombs_group, self.type, spd_scale)

    def die(self):
        if self.kill_time == 0:
            play_sound("alien_dead")
            self.image = self.kill_image
            self.kill_time = self.ALIEN_DEAD_TIME + self.time

    def hit(self):
        self.die()
        return True

class BonusAlien(Alien):
    def __init__(self, pos, spd, sprite_group, bombs_group, kill_x):
        super().__init__(sprite_group, pos, settings.BONUS_ALIEN_TYPE, -1, bombs_group)
        self.spd = spd
        self.kill_x = kill_x
        self.ALIEN_DEAD_TIME = 0.4
        self.animation_spd = 6

    def update(self, dt) -> None:
        super().update(dt)
        if self.kill_time:
            return
        self.x += self.spd * dt
        if (self.x >= self.kill_x >= self.rect.x) or (self.x <= self.kill_x <= self.rect.x):
            self.kill()
        self.rect.x = self.x