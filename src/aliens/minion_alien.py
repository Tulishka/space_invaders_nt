import math
from random import randint, choice

from src import settings, sound
from .alien import Alien
from ..core.cooldown import Cooldown


class MinionAlien(Alien):
    """Класс миньона"""

    def __init__(self, scene_groups: dict, pos: tuple[float, float], type_: str, move_target_x: float):
        """
        :param scene_groups: Спрайты сцены.
        :param pos: Позиция пришельца
        :param type_: Тип пришельца.
        :param move_target_x: Координата х для точки патрулирования
        """
        super().__init__(scene_groups, pos, type_, 0, 0.2, size=0.5)
        self.shot_cooldown = Cooldown(self, settings.MINION_BASE_SHOT_COOLDOWN, 1, started=True)
        self.retarget_cooldown = Cooldown(self, 4.5, 3)
        self.set_target(move_target_x)
        self.radius = randint(36, 80)
        self.radius_spd = randint(2, 4) * 0.3
        self.radius_dir = choice((-1, 1))
        self.radius_k = - self.radius

    def update(self, dt):
        """Обновление состояния миньона"""
        super().update(dt)

        self.warp_x *= 0.97
        self.warp_y *= 0.97
        if abs(self.warp_x) > 20:
            if self.radius_k > -self.radius:
                self.radius_k -= dt * 100
        else:
            if self.radius_k < 0:
                self.radius_k += dt * 100
        radius = self.radius + self.radius_k
        a = self.time * self.radius_spd * self.radius_dir
        self.set_rect_xy(
            self.x + self.warp_x + radius * math.cos(a) - self.image.get_width() // 2,
            self.y + self.warp_y + radius * math.sin(a) - self.image.get_height() // 2,
        )

    def can_set_target(self) -> bool:
        """Проверка возможности сменить цель

        :return: True - если миньону можно задать новую цель
        """
        return self.retarget_cooldown()

    def set_target(self, move_target_x):
        """Смена цели (координата x, над которой патрулирует миньон)"""
        if abs(move_target_x - self.x) > 250:
            sound.play_sound("minion_relocate")
        self.warp_x = self.x - move_target_x
        self.x = move_target_x
        self.retarget_cooldown.start()
