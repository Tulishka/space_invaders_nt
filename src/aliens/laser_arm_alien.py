import pygame

from src.aliens import Alien
from src.aliens.alien import AlienState
from src.components.projectile import Beam
from src.core.animation import update_animations_images


class AlienLaserArm(Alien):
    """Класс лазерной руки (пушки)"""

    def __init__(self, scene_groups: dict, left_side=True):
        """
        :param scene_groups: группы спрайтов сцены
        :param left_side: True - если это пушка слева
        """
        super().__init__(scene_groups, (0, 0), "7_arm", 0)
        if not left_side:
            # Если это не левая сторона (рука), перевернем все изображения вдоль X
            for image, set_image in update_animations_images(self.animations):
                set_image(pygame.transform.flip(image, True, False))

            self.image = self.animations[self.state][0]

        # левая "рука"
        self.left_side = left_side

        # расстояния на которое выдвигается пушка
        self.extend_range = 13
        self.parent = None
        self.type = 8
        self.animations[AlienState.IDLE].fps = 4

        # храним спрайт луча (тип Beam)
        self.laser = None

        # подготовка к выстрелу, изменяется от 0 до 1
        self.charge = 0

    def update(self, dt):
        """Обновление состояния"""
        super().update(dt)

        if not self.parent:
            return

        if not self.is_dead() and self.parent.is_dead():
            self.stop_beam_laser()
            self.die()

        if self.is_dead():
            return

        if self.left_side:
            self.x = self.parent.x - (self.extend_range * self.charge + 4)
        else:
            self.x = self.parent.x + self.parent.rect.width // 2 + (self.extend_range * self.charge + 4)
        self.y = self.parent.y + 15

        if self.parent.special2:
            if not self.laser or not self.laser.alive():
                self.laser = Beam((0, 0), "laser", 0, self.scene_groups["bombs"])

        elif self.laser:
            self.stop_beam_laser()

        st = (self.parent.special1 - self.charge) * 3 * dt
        self.charge += st
        if self.charge > 1:
            self.charge = 1
        elif self.charge < 0:
            self.charge = 0

    def set_rect_xy(self, x, y):
        """Обновляет позицию спрайта"""
        super().set_rect_xy(x, y)
        if self.laser:
            self.laser.rect.midtop = self.rect.centerx - (7 if self.left_side else -8), self.rect.centery + 10

    def kill(self):
        """Обработчик удаления спрайта из сцены"""
        super().kill()
        self.stop_beam_laser()
        self.shield_down()

    def stop_beam_laser(self):
        """Отключение лазера"""
        if self.laser:
            if self.laser.alive():
                self.laser.kill()
            self.laser = None

    def set_parent(self, alien: Alien):
        """Задаёт пришельца-родителя для лазерной пушки"""
        self.parent = alien
        self.warp_y = alien.warp_y
        self.time = alien.time
        self.warp_time = alien.warp_time

    def shot(self, spd_scale: float = 1):
        """Для лазерной руки этот метод ничего не делает"""
        pass
