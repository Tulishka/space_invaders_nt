import math
import random

import pygame

import settings
import sound
from alien import Alien
from minion_alien import MinionAlien
from scene_manager import SceneManager


class AlienBoss(Alien):
    MINION_ALIEN_TYPES = (1, 2, 3)

    def __init__(self, aliens_group, pos, player_group, bombs_group):
        super().__init__(aliens_group, pos, settings.BOSS_ALIEN_TYPE, -1, bombs_group, 0.3)
        self.player_group = player_group
        self.max_hp = 100 * len(self.player_group)
        self.hp = self.max_hp
        self.warp_y = -500
        self.minions_spawn_time = 4.5
        self.positions = [
            pos,
            (pos[0] - 250, pos[1] - 100),
            (pos[0] + 100, pos[1] + 150),
            (pos[0] + 250, pos[1] - 100),
            (pos[0] - 100, pos[1] + 150),
        ]
        self.spawn_rate = [1, 1, 2, 1, 1.5]
        self.spawn_players_rate = max(len(player_group) * 0.75, 1)
        self.current_pos = 0
        self.next_pos_time = self.time + random.randint(6, 12)
        self.boss_next_online = 15
        self.spd = 0
        self.move_time = 0

    def move(self, dt):
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
            sound.play_sound("boss_move")

        ly = self.rect.bottom
        x = self.x + 10 * math.cos(self.time + self.time * abs(math.cos(self.time * 0.5)) * 0.05)
        y = self.y + self.warp_y + 10 * math.sin(self.time + self.time * abs(math.sin(self.time * 0.2)) * 0.05)
        self.rect = self.image.get_rect(center=(x, y))

        if ly < 0 <= self.rect.bottom:
            sound.play_sound("boss_signal")

    def spawn_minion(self):
        max_minions = settings.MINIONS_COUNT * self.spawn_players_rate
        if self.minions_spawn_time < self.time and len(self.aliens_group) <= max_minions:
            x, y = self.rect.midbottom

            if self.time > self.boss_next_online:
                sound.play_sound("boss_online")
                self.boss_next_online = self.time + 30

            m = MinionAlien(
                self.aliens_group,
                (x, y),
                random.choice(self.MINION_ALIEN_TYPES),
                0,
                self.bombs_group,
                x + random.uniform(-10.0, 10.0)
            )
            sound.play_sound("minion_warp")
            m.warp_y = - random.randint(50, 150)
            m.y -= m.warp_y
            m.y = min(m.y, settings.SCREEN_HEIGHT - 150)
            self.minions_spawn_time = self.time + settings.MINIONS_SPAWN_COOLDOWN * (
                    1 / (self.spawn_rate[self.current_pos] * self.spawn_players_rate))
        elif self.minions_spawn_time < self.time:
            self.minions_spawn_time = self.time + settings.BOSS_RESPAWN_MINIONS_COOLDOWN

    def update_minions(self, dt):
        players = [player for player in self.player_group if not player.dead]
        for alien in self.aliens_group:
            if alien is not self:
                alien.update(dt)
                if alien.type in AlienBoss.MINION_ALIEN_TYPES and alien.can_set_target() and players:
                    min_d = alien.time - alien.target_time > 8 or min(
                        abs(player.rect.center[0] - alien.x) for player in players) > 10
                    if min_d:
                        alien.set_target(random.choice(players).rect.center[0])

    def update(self, dt):
        warp = self.time < self.spawn_time
        super().update(dt)
        if warp and self.time >= self.spawn_time:
            sound.play_sound("boss_online")
        self.warp_y *= 0.99

        if not self.kill_time and self.alive():
            self.move(dt)
            if not warp:
                self.spawn_minion()

        self.update_minions(dt)

    def hit(self):
        if self.time < self.spawn_time:
            return False

        self.hp -= 1
        if self.kill_time == 0 and self.hp <= 0:
            self.die()
            return True

        return self.hp > 0
