import math

from pygame import Vector2

from .alien import Alien
from .. import settings


class SceneAlien(Alien):
    """Класс реализует пришельца для анимаций в меню"""

    def __init__(self, scene_groups: dict, pos: tuple[int, int], type_: str, column,
                 spd: tuple[int, int], warp_time: float = 0,
                 warp_spd: int = 0):
        super().__init__(scene_groups, pos, type_, column, warp_time)
        self.spd = math.hypot(spd[0], spd[1])
        self.direction = Vector2(spd).normalize()
        self.warp_spd = warp_spd
        self.animation_spd = 6 if type_ == 4 else 2

    def update(self, dt):
        """Обновление состояния пришельца
        :param dt: время, сек
        :return None:
        """
        super().update(dt)

        # движение в заданном направлении
        # self.warp_spd - начальная высокая скорость, замедляется со временем
        spd = self.direction * max(self.spd, self.warp_spd) * dt
        self.x += spd.x
        self.y += spd.y

        self.rect.center = self.x, self.y
        self.warp_spd *= 0.7
        if (
                self.rect.right < 0 or self.rect.left > settings.SCREEN_WIDTH or
                self.rect.bottom < 0 or self.rect.top > settings.SCREEN_HEIGHT
        ):
            # уничтожение пришельца, если он находится за границами экрана и отдаляется от центра экрана
            x, y = self.x - settings.SCREEN_WIDTH // 2, self.y - settings.SCREEN_HEIGHT // 2
            center_dest = math.hypot(x, y)
            next_center_dest = math.hypot(x + spd.x, y + spd.y)
            if next_center_dest > center_dest:
                self.kill()
