import random
from collections import defaultdict
from functools import partial

import pygame

from src import settings, music
from src.aliens import SceneAlien
from src.aliens.alien import AlienState
from src.components.particles import create_particle_explosion
from src.components.player import Player
from src.components.projectile import Bomb, Bullet
from src.components.projectile_utils import collide_bullets
from src.core import db, pg_utils, web_results, images
from src.core.cooldown import Cooldown
from src.core.pg_utils import create_text_sprite, create_table, create_text_image
from src.core.scene import Scene
from src.core.scene_manager import SceneManager
from src.menu import Menu, ImageMenuItem, MarginMenuItem


class ScoresScene(Scene):
    """Класс сцены зал славы"""

    music_theme = "ost_rus"

    def __init__(self, scene_manager: SceneManager, params: dict = None):

        self.scene_groups = defaultdict(pygame.sprite.Group)
        self.scene_groups["bombs"].empty()
        self.scene_groups["aliens"].empty()
        self.scene_groups["particles"].empty()
        self.scene_groups["bullets"].empty()
        self.scene_groups["table"].empty()
        self.scene_groups["logo"].empty()

        super().__init__(scene_manager, params)
        self.back_image = images.load("game_back.jpg")
        self.back_image_top = 0
        self.hidden_height = 0

        results = db.get_top_results(10)

        table_width = 550

        tab_rect = pygame.Rect(settings.SCREEN_WIDTH // 2 - table_width // 2, 260,
                               table_width, settings.SCREEN_HEIGHT - 400)

        logo = create_text_sprite(self.scene_groups["logo"], "SPACE INVADERS", font_size=60, color="yellow")
        logo.rect.center = (settings.SCREEN_WIDTH // 2, 100)

        label = create_text_sprite(self.scene_groups["logo"], "НОВАЯ УГРОЗА", font_size=40)
        label.rect.midtop = settings.SCREEN_WIDTH // 2, logo.rect.bottom

        if results:
            text1 = create_text_sprite(self.scene_groups["logo"], "ЛОКАЛЬНЫЙ ТОП-10", font_size=32, color="green")
            text1.rect.midtop = settings.SCREEN_WIDTH // 2, label.rect.bottom + 40

            create_table(results, tab_rect, self.scene_groups["table"], spacing=8)
        else:
            no_results = create_text_sprite(self.scene_groups["logo"], "пока нет результатов игр", font_size=28,
                                            color="white")
            no_results.rect.midtop = tab_rect.midtop

        self.menu = Menu()
        self.menu.spacing = 12
        self.menu.top = settings.SCREEN_HEIGHT - 220
        self.menu.no_back = True
        self.menu.selected = ImageMenuItem(
            self.menu, create_text_image(
                "ОТКРЫТЬ МИРОВЫЕ РЕКОРДЫ", font_size=26,
                color=(200, 200, 255)
            ),
            action=web_results.open_world_records)
        MarginMenuItem(self.menu, 2)
        ImageMenuItem(self.menu, create_text_image("саундтреки написанные для игры", font_size=26, color="gray"))
        ImageMenuItem(
            self.menu,
            create_text_image("Вторжение пришельцев (rus)", font_size=28, color="green"),
            partial(self.set_music_theme, "ost_rus")
        )
        ImageMenuItem(
            self.menu, create_text_image("Space Invasion (eng)", font_size=28, color="green"),
            partial(self.set_music_theme, "ost_eng")
        )
        MarginMenuItem(self.menu, 0)
        ImageMenuItem(self.menu, create_text_image("ВЫХОД", font_size=28, color=(200, 200, 255)), self.exit)

        self.alien_spawn_cd = Cooldown(self, 0.5, 0.2)
        self.alien_shot_cd = Cooldown(self, 0.8, 0.2)
        self.shot_cd = Cooldown(self, 0.3, 0.2)
        self.accurate_shot_cd = Cooldown(self, 0.5, 0.3)

        ScoresScene.music_theme = db.get_var("music_theme") or ScoresScene.music_theme
        self.music_theme_cd = Cooldown(self, 0.1)

    def on_show(self, first_time):
        """Обработчик события включения сцены.
        :param first_time: True если сцена появилась первый раз.
        :return None:
        """
        super().on_show(first_time)
        self.music_theme_cd.start()
        self.alien_spawn_cd.start()
        self.alien_shot_cd.start()
        self.shot_cd.start(10)
        self.accurate_shot_cd.start(13)

    def draw(self, screen):
        """Отрисовка сцены.
        :param screen: Поверхность на которой рисовать.
        :return None:
        """
        screen.blit(self.back_image, (0, self.back_image_top))

        for group in self.scene_groups.values():
            group.draw(screen)

        self.menu.draw(screen)

    def add_alien(self, y):
        """Добавление пришельца в сцену"""
        alien = SceneAlien(
            self.scene_groups,
            (random.randint(100, settings.SCREEN_WIDTH - 100), y),
            random.choice((1, 2, 3, 7)),
            0,
            (0, random.randint(30, 60))
        )

        alien.animations[AlienState.IDLE].images = [
            pg_utils.darken_image(img, 0.75) for img in alien.animations[AlienState.IDLE].images
        ]
        alien.image = alien.animations[alien.state][0]
        alien.last_shot = 0

    def update(self, dt):
        """Обновление состояния сцены.
        :param dt: Время с прошлого выполнения этой функции.
        :return None:
        """
        super().update(dt)

        if self.music_theme_cd:
            music.play(ScoresScene.music_theme, 1, 0)
            self.music_theme_cd.start(99999999)

        for group in self.scene_groups.values():
            group.update(dt)

        if self.alien_spawn_cd:
            self.alien_spawn_cd.start()
            self.add_alien(-32)

        if self.alien_shot_cd:
            self.alien_shot_cd.start()
            sh = []
            for alien in self.scene_groups["aliens"]:
                if settings.SCREEN_HEIGHT - 100 > alien.y >= 50:
                    sh.append((alien.last_shot, alien))
            if sh:
                alien = sorted(sh, key=lambda x: x[0])[0][1]
                b = Bomb(alien.rect.midbottom, self.scene_groups["bombs"], alien.type, 0.3)
                b.image = pg_utils.darken_image(b.image, 0.5)
                alien.last_shot = self.time

        if self.shot_cd:
            self.shot_cd.start()
            x = random.randint(100, settings.SCREEN_WIDTH - 100)
            Bullet((x, settings.SCREEN_HEIGHT), self.scene_groups["bullets"], None)
        elif self.accurate_shot_cd:
            self.accurate_shot_cd.start()
            bottom_alien = None
            for alien in self.scene_groups["aliens"]:
                if alien.y > settings.SCREEN_HEIGHT - 300 and (not bottom_alien or alien.y < bottom_alien.y):
                    bottom_alien = alien
            if bottom_alien:
                Bullet((bottom_alien.rect.centerx, settings.SCREEN_HEIGHT), self.scene_groups["bullets"], None)

        collide_bullets(self.scene_groups, self.hit_alien)

    def hit_alien(self, alien, player: Player = None):
        """Обработка попадания в пришельца"""
        alien.image = alien.animations[AlienState.WARP][0]
        alien.kill_time = alien.time + 0.15
        alien.state = AlienState.DEAD
        create_particle_explosion(
            self.scene_groups["particles"], alien, 24, (2, 5),
            50, (0, alien.spd), 1.5
        )

    def process_event(self, event):
        """Обработка событий pygame
        :param event: Событие pygame
        :return None:
        """
        if self.menu.process_event(event):
            return

        if self.time > settings.SCENE_KEY_COOLDOWN and event.type == pygame.KEYDOWN and event.key in (
                pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN):
            self.exit()

    def set_music_theme(self, theme_name):
        """Сменяет музыку"""
        ScoresScene.music_theme = theme_name
        db.set_var("music_theme", theme_name)
        self.music_theme_cd.start()

    def exit(self):
        """Выходит из сцены"""
        self.scene_manager.pop_scene()
