import random
import sys
from functools import partial

import pygame

from src import music, settings
from src.aliens import MenuAlien
from src.core.scene import Scene
from src.menu import Menu, ImageMenuItem, MarginMenuItem
from src.sound import play_sound


class MenuScene(Scene):
    def __init__(self, scene_manager, params=None):
        super().__init__(scene_manager, params)
        font3 = pygame.font.Font(None, 40)

        p1 = font3.render("1 - игрок", True, "green")
        p2 = font3.render("2 - игрока", True, "green")

        p3 = pygame.Surface(p2.get_size(), flags=pygame.SRCALPHA)
        p3.blit(p1, (0, 0))
        p1 = p3

        self.menu = Menu()
        ImageMenuItem(self.menu, pygame.image.load(f'./img/logo.png'))
        MarginMenuItem(self.menu, 10)
        self.menu.selected = ImageMenuItem(self.menu, p1, partial(self.start_game, 1),pygame.K_1)
        ImageMenuItem(self.menu, p2, partial(self.start_game, 2),pygame.K_2)
        ImageMenuItem(self.menu, font3.render("рекорды", True, "green"), self.open_results)
        ImageMenuItem(self.menu, font3.render("выход", True, "green"),sys.exit)

        self.markers = self.load_markers("music/menu1_markers.txt")
        self.cur_marker = 0
        self.beat_value = 0
        self.aliens_group = pygame.sprite.Group()
        self.front_group = pygame.sprite.Group()
        self.bonus_alien_beat_num = 4

        self.back_image = pygame.image.load("img/menu_back.jpg")

    def replay_scene(self):
        music.play("menu")
        self.time = 0
        self.cur_marker = 0

    def on_show(self, first_time):
        play_sound("menu_show")

        # для анимации фона
        self.aliens_group.empty()

        self.replay_scene()
        self.time = 0

    def on_hide(self):
        music.stop()

    def draw(self, screen):
        screen.blit(self.back_image, (0, 0))

        self.aliens_group.draw(screen)
        self.front_group.draw(screen)
        self.menu.selection_extend_x = 25 + 30 * self.beat_value * (self.time > 5)
        self.menu.draw(screen)

    def update(self, dt):
        super().update(dt)

        self.beat_value *= 0.95 - (0.2 * dt)
        if self.cur_marker < len(self.markers) and self.markers[self.cur_marker] <= self.time:
            self.beat_value = 1
            self.cur_marker += 1
            pos = (settings.SCREEN_WIDTH, random.randint(32, settings.SCREEN_HEIGHT - 32))

            if self.bonus_alien_beat_num == self.cur_marker or self.cur_marker % 30 == 0:
                alien_type = settings.BONUS_ALIEN_TYPE
                spd = 200
            else:
                alien_type = random.randint(1, 2)
                spd = random.randint(50, 120)

            MenuAlien(self.aliens_group, pos, alien_type, 0, self.front_group, spd, 0.2 * (self.time > 5))

        self.aliens_group.update(dt)
        self.menu.update(dt)

    def start_game(self, num_players, level=1):
        self.scene_manager.kill_scene("trailer")
        self.scene_manager.set_scene("trailer", {
            "num_players": num_players,
            "level": level,
            "lives": settings.PLAYER_START_LIVES,
        })
        play_sound("menu_start")

    def process_event(self, event):

        if event.type == settings.MUSIC_END_EVENT:
            self.replay_scene()

        if self.menu.process_event(event):
            return

        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_5:
            self.start_game(1, 5)
        if event.key == pygame.K_6:
            self.scene_manager.kill_scene("boss")
            self.scene_manager.set_scene("boss", {
                "num_players": 2,
                "level": 1,
                "lives": settings.PLAYER_START_LIVES,
            })

        if self.time > settings.KEY_COOLDOWN and event.key == pygame.K_ESCAPE:
            return "exit"

    def load_markers(self, filename):
        with open(filename, "r") as f:
            lines = f.readlines()
            return [float(i) for i in lines]

    def open_results(self):
        pass
