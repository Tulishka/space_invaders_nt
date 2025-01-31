import math
import random

from src import settings, sound
from .alien import Alien, HpAlienMixin


class AcolyteAlien(HpAlienMixin, Alien):

    def __init__(self, scene_groups, pos, direction=1):
        super().__init__(scene_groups, pos, settings.ACOLYTE_ALIEN_TYPE, -1, 0.3)
        self.hp = settings.ACOLYTE_ALIEN_HP
        self.warp_y = -200
        self.spd = 100
        self.direction = direction
        self.boost_spd = 0
        self.protect_cooldown = 1.3
        self.give_shield_cooldown = 4
        self.animation_spd = 4
        self.set_rect_xy(self.x, self.y + self.warp_y)
        self.protect_alien_types = (1, 2, 3, 7)
        self.boost = 0

    def protect_minions(self, dt):
        self.give_shield_cooldown -= dt
        if self.give_shield_cooldown <= 0:
            self.give_shield_cooldown = self.protect_cooldown

            minions = [alien for alien in self.scene_groups["aliens"] if
                       not alien.is_dead() and not alien.has_shield() and alien.type in self.protect_alien_types]
            if minions:
                minion = random.choice(minions)
                minion.shield_up()
                sound.play_sound("alien_shield_up")
                self.boost = 10

    def update(self, dt):
        warp = self.time < self.spawn_time
        super().update(dt)

        if warp and self.time >= self.spawn_time:
            sound.play_sound("alien_warp")
        self.warp_y *= 0.99

        if self.warp_y > 0.01:
            return

        step = (self.spd + 30 * math.cos(self.time * 2)) * self.direction * dt
        if self.rect.right + step > settings.SCREEN_WIDTH or self.rect.left + step < 0:
            self.direction *= -1
        else:
            self.x += step

        x = self.x + 10 * math.cos(self.time + self.time * abs(math.cos(self.time * 0.5)) * 0.05) + 3 * math.cos(self.boost)
        y = (self.y + self.warp_y + 10 * math.sin(
            self.time + self.time * abs(math.sin(self.time * 0.2)) * 0.05) + 15 * math.sin(self.time * 2))
        self.set_rect_xy(x, y)

        self.boost *= 0.8

        if not self.kill_time and self.alive():
            self.protect_minions(dt)
