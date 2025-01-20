import pygame
from pygame.sprite import Sprite


class Projectile(Sprite):
    def __init__(self, pos: tuple, img_name, spd, sprite_group):
        super().__init__(sprite_group)
        # self.sprite = pygame.sprite.Sprite(sprite_group)
        self.image = pygame.image.load(f'./img/{img_name}.png')
        self.rect = self.image.get_rect(center=pos)
        self.spd = spd


class Bullet(Projectile):
    BULLET_SPEED = -1000

    def __init__(self, pos: tuple, sprite_group, player):
        super().__init__(pos, f'bullet{player.num}', self.BULLET_SPEED, sprite_group)
        self.player = player


class Bomb(Projectile):
    BULLET_SPEED = 300

    def __init__(self, pos: tuple, sprite_group, alient_type, spd_scale=1):
        super().__init__(pos, f'bomb{alient_type}', (self.BULLET_SPEED + 200 * alient_type) * spd_scale, sprite_group)
