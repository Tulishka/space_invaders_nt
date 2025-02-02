import math
from collections import Counter
from random import random, randint, choice

from src import settings, sound
from .alien import Alien
from ..core.cooldown import Cooldown
from ..sound import play_sound


class MinionAlien(Alien):

    def __init__(self, scene_groups, pos, type_, column, move_target_x):
        super().__init__(scene_groups, pos, type_, column, 0.2, size=0.5)
        self.shot_cooldown = Cooldown(self, settings.MINION_BASE_SHOT_COOLDOWN, 1)
        self.retarget_cooldown = Cooldown(self, 4.5, 3)
        self.set_target(move_target_x)
        self.radius = randint(36, 80)
        self.radius_spd = randint(2, 4) * 0.3
        self.radius_dir = choice((-1, 1))
        self.radius_k = - self.radius

    def update(self, dt):
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
        zones = Counter(b.rect.centerx // 333 for b in self.scene_groups["bombs"])
        zones.subtract(player.rect.centerx // 333 for player in self.scene_groups["players"] if not player.dead)
        if self.shot_cooldown and zones[self.rect.centerx // 333] + 1 < settings.MINIONS_MAX_BOMBS:
            for player in self.scene_groups["players"]:
                if not player.dead and abs(self.rect.centerx - player.rect.centerx) < player.rect.width // 2:
                    self.shot(0.5)
                    sound.play_sound("minion_shot")
                    self.shot_cooldown.start()
                    break

    def shield_down(self):
        res = super().shield_down()
        if res:
            play_sound("alien_shield_down")
        return res

    def can_set_target(self):
        return self.retarget_cooldown()

    def set_target(self, move_target_x):
        if abs(move_target_x - self.x) > 250:
            sound.play_sound("minion_relocate")
        self.warp_x = self.x - move_target_x
        self.x = move_target_x
        self.retarget_cooldown.start()
