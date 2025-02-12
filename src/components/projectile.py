import pygame
from pygame.sprite import Sprite

from src import settings
from src.core import images


class Projectile(Sprite):
    """Базовый класс для снарядов"""

    def __init__(self, pos: tuple, img_name, spd, sprite_group):
        super().__init__(sprite_group)
        self.image = images.load(f'{img_name}.png')
        self.rect = self.image.get_rect(center=pos)
        self.spd = spd

    def update(self, dt):
        self.rect.y += self.spd * dt
        if self.rect.y > settings.SCREEN_HEIGHT or self.rect.y < 0:
            self.kill()


class Bullet(Projectile):
    """Снаряд выпускаемый игроком"""

    BULLET_SPEED = -1000

    def __init__(self, pos: tuple, sprite_group, player):
        super().__init__(pos, f'bullet{1 if player is None else player.num}', self.BULLET_SPEED, sprite_group)
        self.player = player


class Bomb(Projectile):
    """Снаряд выпускаемый пришельцем"""

    BULLET_SPEED = 300
    MAX_BULLET_SPEED = 1200

    def __init__(self, pos: tuple, sprite_group, alient_type, spd_scale=1):
        super().__init__(pos, f'bomb{alient_type}',
                         min(self.MAX_BULLET_SPEED, (self.BULLET_SPEED + 110 * alient_type) * spd_scale), sprite_group)


class Beam(Projectile):
    """Класс для реализации энергетического луча"""
    pass
