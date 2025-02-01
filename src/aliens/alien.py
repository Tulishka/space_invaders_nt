import random

import pygame
from pygame.sprite import Sprite
from pygame.transform import scale

from src.components.projectile import Bomb, Beam
from src.sound import play_sound


class Alien(Sprite):
    ALIEN_DEAD_TIME = 0.25

    def __init__(self, scene_groups, pos, type_, column, spawn_time=0, size=1):
        super().__init__(scene_groups["aliens"])
        self.scene_groups = scene_groups
        self.type = type_
        self.images = [
            pygame.image.load(f'./img/enemy{self.type}.png'),
            pygame.image.load(f'./img/enemy{self.type}b.png'),
        ]
        self.kill_image = pygame.image.load(f'./img/enemy{self.type}k.png')
        if size != 1:
            self.kill_image = scale(
                self.kill_image, (self.kill_image.get_width() * size, self.kill_image.get_height() * size)
            )
            self.images = [
                scale(image, (image.get_width() * size, image.get_height() * size))
                for image in self.images
            ]

        self.shield_sprite = None

        self.image = self.images[0]
        self.rect = self.image.get_rect(center=pos)
        self.time = random.random()
        self.kill_time = 0
        self.column = column
        self.x, self.y = pos
        self.spawn_time = self.time + spawn_time
        self.spawn_image = self.images[0].copy()
        self.spawn_image.fill((255, 255, 255, 200), rect=self.spawn_image.get_rect(), special_flags=pygame.BLEND_ADD)
        self.warp_x = 0
        self.warp_y = 0
        self.animation_spd = 2
        self.special1 = 0
        self.special2 = 0
        self.size = size

    def create_shield_image(self) -> pygame.Surface:
        return pygame.image.load('./img/shield.png')

    def hit_shield(self) -> bool:
        if self.has_shield():
            self.shield_down()
            return True
        return False

    def shield_up(self):
        if not self.shield_sprite and self.alive() and not self.is_dead():
            self.shield_sprite = Sprite(self.scene_groups["shields"])
            self.shield_sprite.image = self.create_shield_image()
            if self.size != 1:
                self.shield_sprite.image = scale(
                    self.shield_sprite.image,
                    (
                        self.shield_sprite.image.get_width() * self.size,
                        self.shield_sprite.image.get_height() * self.size
                    )
                )
            self.update_shield()

    def update_shield(self):
        if self.shield_sprite:
            self.shield_sprite.rect = self.shield_sprite.image.get_rect(center=self.rect.center)

    def shield_down(self):
        if self.shield_sprite:
            self.shield_sprite.kill()
            self.shield_sprite = None

    def is_dead(self):
        return self.kill_time > 0

    def update(self, dt) -> None:
        self.time += dt

        if self.time < self.spawn_time:
            self.image = self.spawn_image
            return

        if self.kill_time > 0:
            self.image = self.kill_image
            if self.time > self.kill_time:
                self.kill()
        else:
            self.image = self.images[int(self.time * self.animation_spd + self.type * 0.5) % len(self.images)]

    def die(self):
        if self.kill_time == 0:
            play_sound("alien_dead")
            self.kill_time = self.ALIEN_DEAD_TIME + self.time

    def hit(self):
        if self.hit_shield():
            return False

        if self.kill_time == 0:
            self.die()
            return True

        return False

    def shot(self, spd_scale=1):
        if not self.is_dead():
            Bomb(self.rect.midbottom, self.scene_groups["bombs"], self.type, spd_scale)

    def set_rect_xy(self, x, y):
        self.rect.x, self.rect.y = (x, y)
        self.update_shield()

    def has_shield(self):
        return self.shield_sprite is not None


class AlienLaserArm(Alien):
    def __init__(self, scene_groups, pos, type_, column, spawn_time=0, size=1, left_side=True):
        super().__init__(scene_groups, pos, type_, column, spawn_time, size)
        if not left_side:
            self.images = [pygame.transform.flip(img, True, False) for img in self.images]
            self.kill_image = pygame.transform.flip(self.kill_image, True, False)
            self.spawn_image = pygame.transform.flip(self.spawn_image, True, False)
            self.image = self.images[0]
        self.left_side = left_side
        self.extended = 0
        self.extend_range = 13
        self.parent = None
        self.type = 8
        self.animation_spd = 4
        self.laser = None
        self.charge = 0

    def update(self, dt):
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
        super().set_rect_xy(x, y)
        if self.laser:
            self.laser.rect.midtop = self.rect.centerx - (7 if self.left_side else -8), self.rect.centery + 10

    def kill(self):
        super().kill()
        self.stop_beam_laser()
        self.shield_down()

    def stop_beam_laser(self):
        if self.laser:
            if self.laser.alive():
                self.laser.kill()
            self.laser = None

    def set_parent(self, alien):
        self.parent = alien
        self.warp_y = alien.warp_y
        self.time = alien.time
        self.spawn_time = alien.spawn_time

    def shot(self, spd_scale=1):
        pass

    def die(self):
        if self.kill_time == 0:
            self.kill_time = self.time + 0.2



class HpAlienMixin:

    def hit(self):
        if self.time < self.spawn_time:
            return False

        if self.hit_shield():
            return False

        self.hp -= 1
        if self.kill_time == 0 and self.hp <= 0:
            self.die()
            return True

        return self.hp > 0
