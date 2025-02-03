import math
from random import choice, randint, choices

from src import settings
from src.aliens import Alien, AlienLaserArm
from src.aliens.acolyte_alien import AcolyteAlien
from src.components.projectile import Beam
from src.core.cooldown import Cooldown
from src.core.scene_manager import SceneManager
from src.sound import sounds, play_sound


class Swarm:
    SWARM_START_X = 100
    SWARM_START_Y = 70

    ALIEN_X_DISTANCE = 80
    ALIEN_Y_DISTANCE = 50

    LINE_WIDTH = 640
    ALIEN_WIDTH = 64

    def __init__(self, level, scene_groups, scene_manager: SceneManager):
        self.time = 0
        self.scene_groups = scene_groups
        self.ls = settings.level[level]
        self.ALIEN_X_DISTANCE = self.LINE_WIDTH // self.ls.alien_in_line
        self.dir = 0
        self.scene_manager = scene_manager
        self.aliens_group = scene_groups["aliens"]
        self.players_group = scene_groups["players"]
        self.bombs_group = scene_groups["bombs"]
        self.shot_order = self.ls.swarm_shot_order
        self.acolyte = False

        self.shot_cooldown = [
            Cooldown(self, self.ls.swarm_cd, started=True)
            for _ in self.players_group
        ]
        self.shot_order_pos = [0] * len(self.players_group)

        self.min_x = 0
        self.min_y = 0
        self.max_x = 0
        self.max_y = 0

        self.sound_alien_shot = [
            sounds["alien_shot1"],
            sounds["alien_shot2"],
            sounds["alien_shot3"],
            sounds["alien_shot3"],
            sounds["alien_shot3"],
            sounds["alien_shot3"],
            sounds["alien_shot7"],
        ]

        self.alien_start_count = self.create()
        self.swarm_down_warp = 0

        self.special_shot_time = self.time + 6
        self.special_prepare_time = self.special_shot_time - 2
        self.special_aliens = []
        self.beam_on = False

    def special_weapon_init(self):
        for alien in self.special_aliens:
            alien.special1 = 0
            alien.special2 = 0
        self.special_shot_time = self.time + randint(5, 10)
        self.special_prepare_time = self.special_shot_time - 2
        self.special_aliens = []

    def special_shot(self, on):
        for alien in self.special_aliens:
            alien.special2 = on

    def special_prepare(self, aliens):
        if len(aliens) > 0:
            idx1 = randint(0, len(aliens) - 1)
            idx2 = (idx1 + len(aliens) // 2) % len(aliens)
            self.special_aliens = [aliens[idx1], aliens[idx2]]
            for alien in self.special_aliens:
                alien.special1 = 1
        else:
            self.special_aliens = []

    def create(self):
        x0 = self.SWARM_START_X
        y0 = self.SWARM_START_Y

        lines = len(self.ls.alien_types)
        cnt = 0

        for y, typ in enumerate(self.ls.alien_types):
            for x in range(self.ls.alien_in_line):
                if typ == settings.HEAVY_ALIEN_TYPE:
                    l_arm = AlienLaserArm(
                        self.scene_groups,
                        (x0 + x * self.ALIEN_X_DISTANCE, y0 + y * self.ALIEN_Y_DISTANCE),
                        "7_arm",
                        x, 0
                    )
                    r_arm = AlienLaserArm(
                        self.scene_groups,
                        (x0 + x * self.ALIEN_X_DISTANCE, y0 + y * self.ALIEN_Y_DISTANCE),
                        "7_arm",
                        x, 0, left_side=False
                    )
                alien = Alien(
                    self.scene_groups,
                    (x0 + x * self.ALIEN_X_DISTANCE, y0 + y * self.ALIEN_Y_DISTANCE),
                    typ,
                    x, 0
                )
                alien.warp_y = -alien.y - 60
                alien.time -= (lines - y) * 0.2 + x * 0.1

                if typ == settings.HEAVY_ALIEN_TYPE:
                    l_arm.set_parent(alien)
                    r_arm.set_parent(alien)

                cnt += 1

        return cnt

    def update(self, dt):
        self.time += dt
        self.min_x = 100000
        self.min_y = 100000
        self.max_x = 0
        self.max_y = 0

        can_shot = [None] * self.ls.alien_in_line
        alive_aliens_count = 0
        for alien in self.aliens_group:
            alien.update(dt)
            if alien.column < 0 or alien.type not in self.ls.alien_types:
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

            if not alien.is_dead() and (can_shot[alien.column] is None or can_shot[alien.column].rect.y < alien.rect.y):
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
                if int(alien.warp_y) == 0 and not isinstance(alien, AlienLaserArm):
                    wp -= 1
            alien.x += px
            alien.y += self.swarm_down_warp * dt
            alien.set_rect_xy(
                alien.x + self.ls.swarm_rot_amp * math.cos(alien.time * self.ls.swarm_rot_spd),
                alien.y + alien.warp_y + 0.2 * self.ls.swarm_rot_amp * math.sin(alien.time * self.ls.swarm_rot_spd)
            )

        if wp == 0 and self.dir == 0:
            self.dir = 1

        if can_shot:
            for idx, player in enumerate(self.players_group):

                if player.dead or not self.shot_cooldown[idx]():
                    continue

                alien_closest_dist = 9999
                accurate = len(can_shot) < settings.SWARM_ALIEN_ACCURATE_SHOT_COUNT
                if self.shot_order[self.shot_order_pos[idx]] or accurate:
                    alien_closest = can_shot[0]
                    for alien in can_shot:
                        d = abs(alien.rect.centerx - player.rect.centerx)
                        if d < alien_closest_dist:
                            alien_closest = alien
                            alien_closest_dist = d
                else:
                    alien_closest = choice(can_shot)

                if (self.shot_order[
                        self.shot_order_pos[idx]] != 2 and not accurate) or alien_closest_dist < player.rect.width // 2:
                    alien_closest.shot()
                    self.shot_cooldown[idx].start()
                    self.sound_alien_shot[alien_closest.type - 1].play()
                    self.shot_order_pos[idx] = (self.shot_order_pos[idx] + 1) % len(self.shot_order)

        if self.time > self.special_prepare_time and not self.special_aliens:
            self.special_prepare([alien for alien in self.aliens_group if alien.type == settings.HEAVY_ALIEN_TYPE])
            self.special_prepare_time += 1000

        if self.time > self.special_shot_time and self.special_aliens:
            if self.time - self.special_shot_time > 2:
                self.special_shot(0)
                if self.time - self.special_shot_time > 3:
                    self.special_weapon_init()
            else:
                self.special_shot(1)

            beams = len([beam for beam in self.bombs_group if isinstance(beam, Beam)])
            if beams and not self.beam_on:
                self.beam_on = True
                sounds["laser_beam"].set_volume(0.5)
                sounds["laser_beam"].play()
            elif not beams and self.beam_on:
                self.beam_on = False
                sounds["laser_beam"].fadeout(300)

        if not self.acolyte and self.ls.acolyte and self.time > 3:
            ac = AcolyteAlien(self.scene_groups, (randint(100, 400), 100), 1)
            ac.hp /= 2
            ac.protect_cooldown = 1.6
            self.acolyte = True
