import random
from collections import defaultdict
from functools import partial

import pygame

from src import settings, music
from src.aliens import SceneAlien
from src.components.particles import create_particle_explosion
from src.components.projectile import DarkBomb, Bullet
from src.components.projectile_utils import collide_bullets
from src.core import db, pg_utils
from src.core.cooldown import Cooldown
from src.core.pg_utils import create_text_sprite, create_table, create_text_image
from src.core.scene import Scene
from src.menu import Menu, ImageMenuItem


class ScoresScene(Scene):
    music_theme = "ost_rus"

    def __init__(self, scene_manager, params=None):

        self.scene_groups = defaultdict(pygame.sprite.Group)
        self.scene_groups["aliens"].empty()
        self.scene_groups["bombs"].empty()
        self.scene_groups["bullets"].empty()
        self.scene_groups["table"].empty()
        self.scene_groups["logo"].empty()

        super().__init__(scene_manager, params)
        self.back_image = pygame.image.load("img/game_back.jpg")
        self.back_image_top = 0
        self.hidden_height = 0

        self.cursor_image = pygame.image.load('./img/cursor.png')

        results = db.get_top_results(10)

        table_width = 550

        tab_rect = pygame.Rect(settings.SCREEN_WIDTH // 2 - table_width // 2, 300,
                               table_width, settings.SCREEN_HEIGHT - 400)

        logo = create_text_sprite(self.scene_groups["logo"], f"SPACE INVADERS", font_size=60, color="yellow")
        logo.rect.center = (settings.SCREEN_WIDTH // 2, 100)

        label = create_text_sprite(self.scene_groups["logo"], f"НОВАЯ УГРОЗА", font_size=40)
        label.rect.midtop = settings.SCREEN_WIDTH // 2, logo.rect.bottom

        text1 = create_text_sprite(self.scene_groups["logo"], f"ТОП-10", font_size=32, color="green")
        text1.rect.midtop = settings.SCREEN_WIDTH // 2, label.rect.bottom + 80

        create_table(results, tab_rect, self.scene_groups["table"], spacing=8)

        self.menu = Menu()
        self.menu.top = settings.SCREEN_HEIGHT - 180
        self.menu.no_back = True
        ImageMenuItem(self.menu, create_text_image("саундтреки созданные в рамках проекта", font_size=26, color="cyan"))
        self.menu.selected = ImageMenuItem(self.menu,
                                           create_text_image("Вторжение пришельцев (rus)", font_size=28, color="green"),
                                           partial(self.set_music_theme, "ost_rus"))
        ImageMenuItem(self.menu, create_text_image("Space Invaders (eng)", font_size=28, color="green"),
                      partial(self.set_music_theme, "ost_eng"))
        ImageMenuItem(self.menu, create_text_image("выход", font_size=28, color="green"), self.exit)

        self.alien_spawn_cd = Cooldown(self, 0.7, 0.3)
        self.alien_shot_cd = Cooldown(self, 0.8, 0.2)
        self.shot_cd = Cooldown(self, 0.5, 0.3)
        self.accurate_shot_cd = Cooldown(self, 0.5, 0.3)

        ScoresScene.music_theme = db.get_var("music_theme") or ScoresScene.music_theme


    def on_show(self, first_time):
        super().on_show(first_time)
        music.play(ScoresScene.music_theme, 1, 0)
        self.alien_spawn_cd.start()
        self.alien_shot_cd.start()
        self.shot_cd.start(10)
        self.accurate_shot_cd.start(20)

    def draw(self, screen):
        screen.blit(self.back_image, (0, self.back_image_top))

        for group in self.scene_groups.values():
            group.draw(screen)

        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[0] != 0 and mouse_pos[1] != 0:
            screen.blit(self.cursor_image, mouse_pos)

        self.menu.draw(screen)

    def add_alien(self, y):
        alien = SceneAlien(
            self.scene_groups,
            (random.randint(100, settings.SCREEN_WIDTH - 100), y),
            random.choice((1, 2, 3, 7)),
            0,
            (0, random.randint(30, 60))
        )
        alien.images = [pg_utils.darken_image(img, 0.9) for img in alien.images]
        alien.image = alien.images[0]
        alien.last_shot = 0

    def update(self, dt):
        super().update(dt)

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
                DarkBomb(alien.rect.midbottom, self.scene_groups["bombs"], 2, 0.3)
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

    def hit_alien(self, alien, player=None):
        alien.image = alien.spawn_image
        alien.kill_time = alien.time + 0.1
        create_particle_explosion(
            self.scene_groups["particles"], alien, 12, (2, 5),
            50, (0, 0), 1.5
        )

    def process_event(self, event):

        if self.menu.process_event(event):
            return

        if self.time > settings.KEY_COOLDOWN and event.type == pygame.KEYDOWN and event.key in (
                pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN):
            self.exit()

    def set_music_theme(self, theme_name):
        ScoresScene.music_theme = theme_name
        db.set_var("music_theme", theme_name)
        self.on_show(0)

    def exit(self):
        self.scene_manager.set_scene("menu")
