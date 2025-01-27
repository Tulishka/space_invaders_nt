import math
from random import choice

from src import settings
from src.aliens import Alien
from src.core.scene_manager import SceneManager
from src.sound import sounds, play_sound


class Swarm:
    SWARM_START_X = 100
    SWARM_START_Y = 70

    ALIEN_X_DISTANCE = 80
    ALIEN_Y_DISTANCE = 50

    LINE_WIDTH = 640
    ALIEN_WIDTH = 64

    def __init__(self, level, aliens_group, scene_manager: SceneManager, players_group, bombs_group):
        self.ls = settings.level[level]
        self.ALIEN_X_DISTANCE = self.LINE_WIDTH // self.ls.alien_in_line
        self.dir = 0
        self.aliens_group = aliens_group
        self.scene_manager = scene_manager
        self.players_group = players_group
        self.bombs_group = bombs_group
        self.shot_cooldown = self.ls.swarm_cd
        self.shot_order = self.ls.swarm_shot_order
        self.shot_order_pos = 0

        self.min_x = 0
        self.min_y = 0
        self.max_x = 0
        self.max_y = 0

        self.sound_alien_shot = [
            sounds["alien_shot1"],
            sounds["alien_shot2"],
            sounds["alien_shot3"],
        ]

        self.alien_start_count = self.create()
        self.swarm_down_warp = 0

    def create(self):
        x0 = self.SWARM_START_X
        y0 = self.SWARM_START_Y

        lines = len(self.ls.alien_types)
        cnt = 0

        for y, typ in enumerate(self.ls.alien_types):
            for x in range(self.ls.alien_in_line):
                alien = Alien(
                    self.aliens_group,
                    (x0 + x * self.ALIEN_X_DISTANCE, y0 + y * self.ALIEN_Y_DISTANCE),
                    typ,
                    x, self.bombs_group, 0
                )
                alien.warp_y = -alien.y - 60
                alien.time -= (lines - y) * 0.2 + x * 0.1
                cnt += 1

        return cnt

    def update(self, dt):
        self.min_x = 100000
        self.min_y = 100000
        self.max_x = 0
        self.max_y = 0

        can_shot = [None] * self.ls.alien_in_line
        alive_aliens_count = 0
        for alien in self.aliens_group:
            alien.update(dt)
            if alien.column < 0:
                continue

            alive_aliens_count += 1
            if alien.time - dt < 0 and alien.time > 0:
                play_sound("alien_warp")

            if alien.rect.left < self.min_x:
                self.min_x = alien.rect.left

            if alien.rect.right > self.max_x:
                self.max_x = alien.rect.right

            if alien.rect.top < self.min_y:
                self.min_y = alien.rect.top

            if alien.rect.bottom > self.max_y:
                self.max_y = alien.rect.bottom

            if can_shot[alien.column] is None or can_shot[alien.column].rect.y < alien.rect.y:
                can_shot[alien.column] = alien

        can_shot = [alien for alien in can_shot if alien is not None]

        spd = (1 - alive_aliens_count / self.alien_start_count) * (
                self.ls.swarm_spd[1] - self.ls.swarm_spd[0]
        ) + self.ls.swarm_spd[0]

        px = spd * dt * self.dir

        self.swarm_down_warp *= 0.95

        old_dir = self.dir

        if self.max_x + px >= settings.SCREEN_WIDTH:
            self.dir = -1

        if self.min_x + px <= 0:
            self.dir = 1

        if old_dir != self.dir:
            self.swarm_down_warp = self.ls.swarm_down_spd * len(self.players_group)

        wp = alive_aliens_count
        for alien in self.aliens_group:
            if alien.column < 0:
                continue

            if alien.time >= 0:
                alien.warp_y *= 0.7
                if int(alien.warp_y) == 0:
                    wp -= 1
            alien.x += px
            alien.y += self.swarm_down_warp * dt
            alien.rect.x = alien.x + self.ls.swarm_rot_amp * math.cos(alien.time * self.ls.swarm_rot_spd)
            alien.rect.y = alien.y + alien.warp_y + 0.2 * self.ls.swarm_rot_amp * math.sin(
                alien.time * self.ls.swarm_rot_spd)

        if wp == 0 and self.dir == 0:
            self.dir = 1

        self.shot_cooldown -= dt
        if self.shot_cooldown < 0:
            self.shot_cooldown = 0

        if can_shot and self.shot_cooldown == 0:
            self.shot_cooldown = self.ls.swarm_cd

            for player in self.players_group:
                if player.dead:
                    continue
                if self.shot_order[self.shot_order_pos]:
                    alien_closest = can_shot[0]
                    for alien in can_shot:
                        if (
                                abs(alien.rect.x - player.rect.x)
                                <
                                abs(player.rect.x - alien_closest.rect.x)
                        ):
                            alien_closest = alien
                else:
                    alien_closest = choice(can_shot)

                alien_closest.shot()
                self.sound_alien_shot[alien_closest.type - 1].play()
                self.shot_order_pos = (self.shot_order_pos + 1) % len(self.shot_order)
