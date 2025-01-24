import math
from random import random, randint, choice

import settings
import sound
from alien import Alien


class MinionAlien(Alien):

    def __init__(self, aliens_group, pos, type_, column, bombs_group, target_x):
        super().__init__(aliens_group, pos, type_, column, bombs_group, 0.2, size=0.5)
        self.target_time = 0
        self.target_x = 0
        self.set_target(target_x)

        self.radius = randint(36, 80)
        self.radius_spd = randint(2, 4) * 0.3
        self.radius_dir = choice((-1, 1))
        self.radius_k = - self.radius
        self.shot_cooldown = 2

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
        self.rect = self.image.get_rect(center=(
            self.x + self.warp_x + radius * math.cos(a),
            self.y + self.warp_y + radius * math.sin(a),
        ))

        if self.shot_cooldown < 0 and abs(self.rect.center[0] - self.x) < 32 and len(self.bombs_group) < settings.MINIONS_MAX_BOMBS:
            self.shot(0.5)
            sound.play_sound("minion_shot")
            self.shot_cooldown = 2+2*random()
        else:
            self.shot_cooldown -= dt

    def can_set_target(self):
        return self.target_time < self.time

    def set_target(self, target_x):
        self.warp_x = self.x - target_x
        self.x = target_x
        self.target_time = self.time + 3 + 3 * random()
