import math
import random

from pygame import Vector2

from .alien import Alien


class SceneAlien(Alien):
    def __init__(self, scene_groups, pos, type_, column, spd: tuple[int, int], spawn_time=0):
        super().__init__(scene_groups, pos, type_, column, spawn_time)
        self.spd = math.hypot(spd[0], spd[1])
        self.direction = Vector2(spd).normalize()
        self.warp_spd = random.randint(1000, 2000)
        self.animation_spd = 6 if type_ == 4 else 2

    def update(self, dt):
        super().update(dt)

        spd = self.direction *max(self.spd, self.warp_spd)
        self.x += spd.x * dt
        self.y += spd.y * dt

        self.rect.center = self.x, self.y
        self.warp_spd *= 0.7
        if self.rect.right < 0:
            self.kill()
