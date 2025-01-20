import random

import pygame
from pygame.sprite import Sprite

from projectile import Bomb


class Alien(Sprite):
    ALIEN_DEAD_TIME = 0.25

    def __init__(self, aliens_group, pos, type_, column, bombs_group):
        super().__init__(aliens_group)
        self.aliens_group = aliens_group
        self.type = type_
        self.image = pygame.image.load(f'./img/enemy{self.type}.png')

        self.rect = self.image.get_rect(center=pos)
        self.time = random.random()
        self.column = column
        self.bombs_group = bombs_group
        self.x, self.y = pos

    def update(self, dt) -> None:
        self.time += dt

    def shot(self, spd_scale=1):
        Bomb(self.rect.midbottom, self.bombs_group, self.type, spd_scale)

    def die(self):
        self.kill()

    def hit(self):
        self.die()
        return True
