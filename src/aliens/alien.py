import random
from enum import Enum

import pygame
from pygame.sprite import Sprite
from pygame.transform import scale

from src.components.projectile import Bomb
from src.core import images
from src.core.animation import Animation, update_animations_images
from src.core.images import load
from src.sound import play_sound


class AlienState(str, Enum):
    IDLE = "idle"
    DEAD = "dead"
    WARP = "warp"


class Alien(Sprite):
    """Основной класс реализующий пришельца"""

    ALIEN_DEAD_TIME = 0.25

    def __init__(
            self, scene_groups: dict,
            pos: tuple[float, float],
            type_: str,
            column: int,
            warp_time: float = 0,
            size: float = 1
    ):
        super().__init__(scene_groups["aliens"])
        self.hp = 1
        self.scene_groups = scene_groups
        self.type = type_
        self.animations: dict[AlienState, Animation] = {
            AlienState.IDLE: Animation([load(f"enemy{self.type}.png"), load(f"enemy{self.type}b.png")]),
            AlienState.DEAD: Animation([load(f"enemy{self.type}k.png")]),
        }

        if size != 1:
            for image, set_image in update_animations_images(self.animations):
                set_image(scale(image, (image.get_width() * size, image.get_height() * size)))

        warp_image = self.animations[AlienState.IDLE][0].copy()
        warp_image.fill((255, 255, 255, 200), rect=warp_image.get_rect(), special_flags=pygame.BLEND_ADD)

        self.state = AlienState.IDLE
        self.animations[AlienState.WARP] = Animation([warp_image])

        self.shield_sprite = None

        self.image = self.animations[self.state][0]
        self.rect = self.image.get_rect(center=pos)

        self.time = random.random()
        self.kill_time = 0
        self.column = column
        self.x, self.y = pos
        self.warp_time = self.time + warp_time
        self.warp_x = 0
        self.warp_y = 0
        self.special1 = 0  # 1 флаг для управления спец средствами, например лазерными пушками
        self.special2 = 0  # 2 флаг для управления спец средствами, например лазерными пушками
        self.size = size

    def create_shield_image(self) -> pygame.Surface:
        """Создает и возвращает изображение щита"""
        return images.load('shield.png')

    def hit_shield(self) -> bool:
        """Обработчик попадания по щиту
        :return bool: вернуть True - если щит защитил, False - если нет.
        """
        if self.has_shield():
            self.shield_down()
            play_sound("alien_shield_down")
            return True
        return False

    def shield_up(self):
        """Метод включает щит"""
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
        """Обновляет позицию щита"""
        if self.shield_sprite:
            self.shield_sprite.rect = self.shield_sprite.image.get_rect(center=self.rect.center)

    def shield_down(self):
        """Метод выключает щит"""
        if self.shield_sprite:
            self.shield_sprite.kill()
            self.shield_sprite = None

    def is_dead(self):
        """Проверяет, убит ли пришелец"""
        return self.kill_time > 0

    def update(self, dt) -> None:
        """Обновление состояния пришельца"""
        self.time += dt

        if self.time < self.warp_time:
            self.state = AlienState.WARP
        else:
            if self.kill_time > 0:
                if self.time > self.kill_time:
                    self.kill()
            else:
                self.state = "idle"

        self.image = self.animations[self.state].get_frame(self.time)

    def die(self):
        """Убивает пришельца"""
        if self.state != AlienState.DEAD:
            self.state = AlienState.DEAD
            if self.hp <= 0:
                play_sound("alien_dead")
            self.kill_time = self.ALIEN_DEAD_TIME + self.time

    def hit(self):
        """Обработчик попадания в пришельца"""
        if self.time < self.warp_time:
            return False

        if self.hit_shield():
            return False

        self.hp -= 1
        if self.kill_time == 0 and self.hp <= 0:
            self.die()
            return True

        return self.hp > 0

    def shot(self, spd_scale=1):
        """Создает выстрел пришельцем"""
        if not self.is_dead():
            Bomb(self.rect.midbottom, self.scene_groups["bombs"], self.type, spd_scale)

    def set_rect_xy(self, x, y):
        """Обновляет позицию для отрисовки спрайта пришельца"""
        self.rect.x, self.rect.y = (x, y)
        self.update_shield()

    def has_shield(self):
        """Проверка активен ли щит"""
        return self.shield_sprite is not None
