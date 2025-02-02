import math

from pygame import Vector2

from .alien import Alien
from .. import settings


class SceneAlien(Alien):
    def __init__(self, scene_groups, pos, type_, column, spd: tuple[int, int], spawn_time: float = 0,
                 warp_spd: int = 0):
        super().__init__(scene_groups, pos, type_, column, spawn_time)
        self.spd = math.hypot(spd[0], spd[1])
        self.direction = Vector2(spd).normalize()
        self.warp_spd = warp_spd
        self.animation_spd = 6 if type_ == 4 else 2
        self.after_init()

    def after_init(self):
        pass

    def update(self, dt):
        super().update(dt)

        spd = self.direction * max(self.spd, self.warp_spd) * dt
        self.x += spd.x
        self.y += spd.y

        self.rect.center = self.x, self.y
        self.warp_spd *= 0.7
        if (
                self.rect.right < 0 or self.rect.left > settings.SCREEN_WIDTH or
                self.rect.bottom < 0 or self.rect.top > settings.SCREEN_HEIGHT
        ):
            x, y = self.x - settings.SCREEN_WIDTH // 2, self.y - settings.SCREEN_HEIGHT // 2
            center_dest = math.hypot(x, y)
            next_center_dest = math.hypot(x + spd.x, y + spd.y)
            if next_center_dest > center_dest:
                self.kill()
