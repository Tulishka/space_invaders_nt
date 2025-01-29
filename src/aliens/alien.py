import random

import pygame
from pygame.sprite import Sprite
from pygame.transform import scale

from src.components.projectile import Bomb
from src.sound import play_sound


class Alien(Sprite):
    ALIEN_DEAD_TIME = 0.25

    def __init__(self, aliens_group, pos, type_, column, bombs_group, spawn_time=0, size=1):
        super().__init__(aliens_group)
        self.aliens_group = aliens_group
        self.type = type_
        self.images = [
            pygame.image.load(f'./img/enemy{self.type}.png'),
            pygame.image.load(f'./img/enemy{self.type}b.png'),
        ]
        self.kill_image = pygame.image.load(f'./img/enemy{self.type}k.png')
        if size != 1:
            self.kill_image = scale(
                self.kill_image, (self.kill_image.get_width() * size, self.kill_image.get_height() * size)
            )
            self.images = [
                scale(image, (image.get_width() * size, image.get_height() * size))
                for image in self.images
            ]

        self.image = self.images[0]
        self.rect = self.image.get_rect(center=pos)
        self.time = random.random()
        self.kill_time = 0
        self.column = column
        self.bombs_group = bombs_group
        self.x, self.y = pos
        self.spawn_time = self.time + spawn_time
        self.spawn_image = self.images[0].copy()
        self.spawn_image.fill((255, 255, 255, 200), rect=self.spawn_image.get_rect(), special_flags=pygame.BLEND_ADD)
        self.warp_x = 0
        self.warp_y = 0
        self.animation_spd = 2

    def update(self, dt) -> None:
        self.time += dt

        if self.time < self.spawn_time:
            self.image = self.spawn_image
            return

        if self.kill_time > 0:
            self.image = self.kill_image
            if self.time > self.kill_time:
                self.kill()
        else:
            self.image = self.images[int(self.time * self.animation_spd + self.type * 0.5) % len(self.images)]

    def die(self):
        if self.kill_time == 0:
            play_sound("alien_dead")
            self.kill_time = self.ALIEN_DEAD_TIME + self.time

    def hit(self):
        if self.kill_time == 0:
            self.die()
            return True

        return False

    def shot(self, spd_scale=1):
        Bomb(self.rect.midbottom, self.bombs_group, self.type, spd_scale)
