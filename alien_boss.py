import math
import random

import pygame

import settings
from alien import Alien


class AlienBoss(Alien):

    def __init__(self, aliens_group, pos, player_group, bombs_group):
        super().__init__(aliens_group, pos, settings.BOSS_ALIEN_TYPE, -1, bombs_group)
        self.player_group = player_group
        self.max_hp = 100 * len(self.player_group)
        self.hp = self.max_hp
        self.positions = [
            pos,
            (pos[0] - 250, pos[1] - 100),
            (pos[0] + 100, pos[1] + 150),
            (pos[0] + 250, pos[1] - 100),
            (pos[0] - 100, pos[1] + 150),
        ]
        self.current_pos = 0
        self.next_pos_time = self.time + random.randint(6, 12)
        self.spd = 0
        self.move_time = 0

    def update(self, dt):
        super().update(dt)

        if not self.kill_time and self.alive():
            vec = pygame.Vector2(self.positions[self.current_pos][0] - self.x,
                                 self.positions[self.current_pos][1] - self.y)

            dist = vec.length()

            if self.spd == 0:
                self.spd = dist / 3
                self.move_time = self.time

            c = (self.time - self.move_time) / 3
            if 0 <= c <= 1:
                spd = self.spd * 4.5 * (1 - c ** c)
            else:
                spd = 20

            if dist > spd * dt:
                vec.scale_to_length(spd)
                self.x += vec.x * dt
                self.y += vec.y * dt
            else:
                self.x = self.positions[self.current_pos][0]
                self.y = self.positions[self.current_pos][1]

            if self.time > self.next_pos_time:
                self.next_pos_time = self.time + random.randint(6, 12)
                self.current_pos = (self.current_pos + 1) % len(self.positions)
                self.spd = 0

            x = self.x + 10 * math.cos(self.time + self.time * abs(math.cos(self.time * 0.5)) * 0.05)
            y = self.y + 10 * math.sin(self.time + self.time * abs(math.sin(self.time * 0.2)) * 0.05)
            self.rect = self.image.get_rect(center=(x, y))

    def hit(self):
        self.hp -= 1
        if self.kill_time == 0 and self.hp <= 0:
            self.die()
            return True

        return self.hp > 0
