import math
from random import choice, randint

from src import settings
from src.aliens import Alien, AlienLaserArm
from src.aliens.acolyte_alien import AcolyteAlien
from src.components.projectile import Beam
from src.core.cooldown import Cooldown
from src.core.scene_manager import SceneManager
from src.sound import sounds, play_sound


class Swarm:
    """Класс реализует рой пришельцев"""
    SWARM_START_X = 100
    SWARM_START_Y = 70

    # расстояния между пришельцами в построении
    ALIEN_X_DISTANCE = 80
    ALIEN_Y_DISTANCE = 50

    # длина линии в построении
    LINE_WIDTH = 640
    ALIEN_WIDTH = 64

    def __init__(self, level: int, scene_groups: dict, scene_manager: SceneManager):
        self.time = 0
        self.scene_groups = scene_groups
        self.ls = settings.level[level]
        self.ALIEN_X_DISTANCE = self.LINE_WIDTH // self.ls.alien_in_line
        self.dir = 0
        self.scene_manager = scene_manager
        self.aliens_group = scene_groups["aliens"]
        self.players_group = scene_groups["players"]
        self.bombs_group = scene_groups["bombs"]
        self.acolyte = False

        self.shot_cooldown = [
            Cooldown(self, self.ls.swarm_cd, started=True)
            for _ in self.players_group
        ]
        self.shot_order = self.ls.swarm_shot_order
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

        self.alive_aliens_count = self.alien_start_count = self.create()
        self.swarm_down_warp = 0

        self.special_shot_time = self.time + 6
        self.special_prepare_time = self.special_shot_time - 2
        self.special_aliens = []
        self.beam_on = False

    def special_weapon_init(self):
        """Подготовка специального оружия (например выстрелы лазера дваарма)"""
        for alien in self.special_aliens:
            alien.special1 = 0
            alien.special2 = 0
        self.special_shot_time = self.time + randint(5, 10)
        self.special_prepare_time = self.special_shot_time - 2
        self.special_aliens = []

    def special_weapon_set_state(self, state: int):
        """Включение/выключение специального оружия (лазеров)"""
        for alien in self.special_aliens:
            alien.special2 = state

    def special_weapon_prepare(self, aliens: list[Alien]):
        """Подготовка специального оружия.
        Выбирает из списка доступных пришельцев двоих избранных.
        Эти пришельцы начнут выдвигать лазерные пушки
        :param aliens: Список доступных пришельцев для применения специального оружия
        """
        if len(aliens) > 0:
            idx1 = randint(0, len(aliens) - 1)
            idx2 = (idx1 + len(aliens) // 2) % len(aliens)
            self.special_aliens = [aliens[idx1], aliens[idx2]]
            for alien in self.special_aliens:
                alien.special1 = 1
        else:
            self.special_aliens = []

    def create(self) -> int:
        """Метод создаёт рой пришельцев
        :return int: количество пришельцев в рое
        """
        x0 = self.SWARM_START_X
        y0 = self.SWARM_START_Y

        lines = len(self.ls.alien_types)
        cnt = 0

        for y, typ in enumerate(self.ls.alien_types):
            for x in range(self.ls.alien_in_line):
                pos = (x0 + x * self.ALIEN_X_DISTANCE, y0 + y * self.ALIEN_Y_DISTANCE)
                if typ == settings.HEAVY_ALIEN_TYPE:
                    l_arm = AlienLaserArm(self.scene_groups, pos, "7_arm", x, 0)
                    r_arm = AlienLaserArm(self.scene_groups, pos, "7_arm", x, 0, left_side=False)
                alien = Alien(self.scene_groups, pos, typ, x, 0)
                alien.warp_y = -alien.y - 60
                # задержка появления пришельцев (в виде отрицательного времени)
                alien.time -= (lines - y) * 0.2 + x * 0.1
                if typ == settings.HEAVY_ALIEN_TYPE:
                    l_arm.set_parent(alien)
                    r_arm.set_parent(alien)
                cnt += 1
        return cnt

    def update(self, dt: float):
        """Обновление состояния роя"""
        self.time += dt

        self.min_x, self.min_y = 100000, 100000
        self.max_x, self.max_y = 0, 0

        can_shot = [None] * self.ls.alien_in_line
        self.alive_aliens_count = 0

        # выясним границы роя, а так же количество живых пришельцев
        for alien in self.aliens_group:
            alien.update(dt)
            if alien.column < 0 or alien.type not in self.ls.alien_types:
                continue

            self.alive_aliens_count += 1
            if (alien.time - dt) < 0 < alien.time:
                play_sound("alien_warp")

            self.min_x = min(self.min_x, alien.rect.left)
            self.max_x = max(self.max_x, alien.rect.right)
            self.min_y = min(self.min_y, alien.rect.top)
            self.max_y = max(self.max_y, alien.rect.bottom)

            if not alien.is_dead() and (can_shot[alien.column] is None or can_shot[alien.column].rect.y < alien.rect.y):
                can_shot[alien.column] = alien

        # Пришельцы, которые могут стрелять (нижний ряд)
        can_shot = [alien for alien in can_shot if alien is not None]
        if can_shot:
            self.shot(can_shot)

        # Расчет скорости роя на основании количества живых пришельцев
        swarm_spd = (1 - self.alive_aliens_count / self.alien_start_count) * (
                self.ls.swarm_spd[1] - self.ls.swarm_spd[0]
        ) + self.ls.swarm_spd[0]
        self.move(swarm_spd, dt)

        self.special_weapon_update()
        self.support_aliens_update()

    def support_aliens_update(self):
        """Спавн прислужника если требуется на этом уровне"""
        if not self.acolyte and self.ls.acolyte and self.time > 3:
            ac = AcolyteAlien(self.scene_groups, (randint(100, 400), 100), 1)
            ac.hp /= 2
            ac.protect_interval = 1.6
            self.acolyte = True

    def move(self, swarm_spd: float, dt: float):
        """Движение роя.
        :param swarm_spd: Скорость роя.
        :param dt: Время в сек.
        :return None:
        """
        px = swarm_spd * dt * self.dir
        self.swarm_down_warp *= 0.95
        old_dir = self.dir

        if self.max_x + px >= settings.SCREEN_WIDTH:
            self.dir = -1
        if self.min_x + px <= 0:
            self.dir = 1

        # При смене направления движения роя, он опускается вниз
        if old_dir != self.dir:
            self.swarm_down_warp = self.ls.swarm_down_spd * len(self.players_group)

        aliens_in_warp_count = self.alive_aliens_count
        for alien in self.aliens_group:
            if alien.column < 0:
                continue
            if alien.time>=0:
                alien.warp_y *= 0.7
                if int(alien.warp_y) == 0 and not isinstance(alien, AlienLaserArm):
                    aliens_in_warp_count -= 1
            alien.x += px
            alien.y += self.swarm_down_warp * dt
            alien.set_rect_xy(
                alien.x + self.ls.swarm_rot_amp * math.cos(alien.time * self.ls.swarm_rot_spd),
                alien.y + alien.warp_y + 0.2 * self.ls.swarm_rot_amp * math.sin(alien.time * self.ls.swarm_rot_spd)
            )

        # когда все пришельцы появились на уровне, рой начинает движение
        if aliens_in_warp_count == 0 and self.dir == 0:
            self.dir = 1

    def shot(self, aliens: list[Alien]):
        """Выбирает пришельца и производит выстрел.
        :param aliens: Пришельцы готовые к стрельбе
        :return None:
        """
        for idx, player in enumerate(self.players_group):
            if player.dead or not self.shot_cooldown[idx]():
                continue
            alien_closest_dist = 9999
            # Условие применения "точного" выстрела
            accurate = len(aliens) < settings.SWARM_ALIEN_ACCURATE_SHOT_COUNT

            if self.shot_order[self.shot_order_pos[idx]] or accurate:
                alien_closest = aliens[0]
                for alien in aliens:
                    dist = abs(alien.rect.centerx - player.rect.centerx)
                    if dist < alien_closest_dist:
                        alien_closest = alien
                        alien_closest_dist = dist
            else:
                alien_closest = choice(aliens)

            if (self.shot_order[self.shot_order_pos[idx]] != 2
                and not accurate) or alien_closest_dist < player.rect.width // 2:
                alien_closest.shot()
                self.shot_cooldown[idx].start()
                self.sound_alien_shot[alien_closest.type - 1].play()
                self.shot_order_pos[idx] = (self.shot_order_pos[idx] + 1) % len(self.shot_order)

    def special_weapon_update(self):
        """Обновление состояния специального оружия, если оно есть на уровне"""

        if self.time > self.special_prepare_time and not self.special_aliens:
            self.special_weapon_prepare(
                [alien for alien in self.aliens_group if alien.type == settings.HEAVY_ALIEN_TYPE])
            self.special_prepare_time += 1000

        if self.time > self.special_shot_time and self.special_aliens:
            if self.time - self.special_shot_time > 2:
                self.special_weapon_set_state(0)
                if self.time - self.special_shot_time > 3:
                    self.special_weapon_init()
            else:
                self.special_weapon_set_state(1)

            beams = len([beam for beam in self.bombs_group if isinstance(beam, Beam)])
            if beams and not self.beam_on:
                self.beam_on = True
                sounds["laser_beam"].set_volume(0.5)
                sounds["laser_beam"].play()
            elif not beams and self.beam_on:
                self.beam_on = False
                sounds["laser_beam"].fadeout(300)
