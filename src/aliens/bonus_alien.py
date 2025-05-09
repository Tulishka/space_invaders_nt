from src import settings
from .alien import Alien, AlienState


class BonusAlien(Alien):
    """Класс бонусного пришельца"""

    def __init__(self, pos, spd, scene_groups, kill_x):
        super().__init__(scene_groups, pos, settings.BONUS_ALIEN_TYPE, -1)
        self.spd = spd
        self.kill_x = kill_x
        self.ALIEN_DEAD_TIME = 0.4
        self.animations[AlienState.IDLE].fps = 6

    def update(self, dt) -> None:
        super().update(dt)
        if self.kill_time:
            return
        self.x += self.spd * dt
        if (self.x >= self.kill_x >= self.rect.x) or (self.x <= self.kill_x <= self.rect.x):
            self.kill()
        self.rect.x = self.x
