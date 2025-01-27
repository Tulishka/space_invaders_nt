import random

from .alien import Alien


class MenuAlien(Alien):
    def __init__(self, aliens_group, pos, type_, column, bombs_group, spd, spawn_time=0):
        super().__init__(aliens_group, pos, type_, column, bombs_group, spawn_time)
        self.spd = spd
        self.warp_spd = random.randint(1000, 2000)
        self.x = self.rect.x
        self.animation_spd = 6 if type_ == 4 else 2

    def update(self, dt):
        super().update(dt)
        self.x -= max(self.spd, self.warp_spd) * dt
        self.rect.x = self.x
        self.warp_spd *= 0.7
        if self.rect.right < 0:
            self.kill()
