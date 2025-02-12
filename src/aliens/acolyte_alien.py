import math
import random

from src import settings, sound
from .alien import Alien
from ..core.cooldown import Cooldown


class AcolyteAlien(Alien):
    """Класс прислужника"""

    def __init__(self, scene_groups: dict, pos: tuple[float, float], direction: int = 1):
        super().__init__(scene_groups, pos, settings.ACOLYTE_ALIEN_TYPE, -1, 0.3)
        self.hp = settings.ACOLYTE_ALIEN_HP
        self.warp_y = -200
        self.spd = 100
        self.direction = direction
        self.animation_spd = 4
        self.set_rect_xy(self.x, self.y + self.warp_y)

        # типы пришельцев кому выдается щит
        self.protect_alien_types = (1, 2, 3, 7)

        # смещение для анимации "встряски" при выдаче щита
        self.boost = 0

        self.give_shield_cooldown = Cooldown(self, 1.3)
        self.give_shield_cooldown.start(2.7)


    def give_shields_to_aliens(self, dt):
        """Основная функция прислужника (раздача щитов).
        :param dt: Время с прошлого выполнения этой функции
        :return None:
        """
        if self.give_shield_cooldown:
            self.give_shield_cooldown.start()
            minions = [
                alien for alien in self.scene_groups["aliens"]
                if not alien.is_dead() and not alien.has_shield() and alien.type in self.protect_alien_types
            ]
            if minions:
                minion = random.choice(minions)
                minion.shield_up()
                sound.play_sound("alien_shield_up")
                # "встряска" прислужника при выдаче щита
                self.boost = 10

    def update(self, dt):
        """Обновление состояния прислужника"""
        warp = self.time < self.warp_time
        super().update(dt)

        if warp and self.time >= self.warp_time:
            sound.play_sound("alien_warp")
        self.warp_y *= 0.99

        if self.warp_y > 0.01:
            return

        # вычисление шага (изменения координаты)
        step = (self.spd + 30 * math.cos(self.time * 2)) * self.direction * dt
        if self.rect.right + step > settings.SCREEN_WIDTH or self.rect.left + step < 0:
            self.direction *= -1
        else:
            self.x += step

        # добавим магические колебания прислужника
        x = self.x + 10 * math.cos(self.time + self.time * abs(math.cos(self.time * 0.5)) * 0.05) + 3 * math.cos(
            self.boost)
        y = (self.y + self.warp_y + 10 * math.sin(
            self.time + self.time * abs(math.sin(self.time * 0.2)) * 0.05) + 15 * math.sin(self.time * 2))
        self.set_rect_xy(x, y)

        self.boost *= 0.8

        if not self.kill_time and self.alive():
            self.give_shields_to_aliens(dt)
