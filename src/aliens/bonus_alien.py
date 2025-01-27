from src import settings
from .alien import Alien


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
