import random

import pygame

from src import music, settings
from src.aliens.alien import MenuAlien
from src.core.scene import Scene
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

        self.menu = [
            (pygame.image.load(f'./img/logo.png'), 30, 0),
            (p1, 20, 1),
            (p2, 20, 2),
            (font3.render("рекорды", True, "green"), 0, 3),
        ]
        self.selected = 1
        self.max_select = 3

        self.markers = self.load_markers("music/menu1_markers.txt")
        self.cur_marker = 0
        self.beat_value = 0
        self.aliens_group = pygame.sprite.Group()
        self.front_group = pygame.sprite.Group()
        self.back = None
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

        start_y = settings.SCREEN_HEIGHT // 2 - 200
        y = start_y
        xc = settings.SCREEN_WIDTH // 2

        for item, py, num in self.menu:
            x = xc - item.get_width() // 2
            screen.blit(item, (x, y))

            if self.selected == num:
                bar_width = 25 + 40 * self.beat_value * (self.time > 5)
                pygame.draw.rect(screen, (0, 200, 0),
                                 pygame.Rect(x - bar_width, y - 5, item.get_width() + 2 * bar_width,
                                             item.get_height() + 10), 2, 25)

            y += item.get_height() + py

        if not self.back:
            height = y - start_y + 40
            width = self.menu[0][0].get_width() + 40
            img = pygame.Surface((width, height), flags=pygame.SRCALPHA)
            rect = img.get_rect(
                center=(xc, start_y + (y - start_y) // 2))
            # img.blit(self.back_image, (0, 0), rect)
            pygame.draw.rect(img, (10, 10, 20), (0, 0, width, height), 0, 8)
            pygame.draw.rect(img, (40, 40, 80), (0, 0, width, height), 2, 8)
            img.set_alpha(200)
            self.back = pygame.sprite.Sprite(self.front_group)
            self.back.image = img
            self.back.rect = rect

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

        if event.type != pygame.KEYDOWN:
            return

        if event.key in (pygame.K_DOWN, pygame.K_s) and self.selected < self.max_select:
            self.selected += 1
            play_sound("menu_beep")
        if event.key in (pygame.K_UP, pygame.K_w) and self.selected > 1:
            self.selected -= 1
            play_sound("menu_beep")
        if self.selected in (1, 2) and event.key in (pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_RETURN):
            self.start_game(self.selected)
        if event.key == pygame.K_1:
            self.start_game(1)
            self.selected = 1
        if event.key == pygame.K_5:
            self.start_game(1, 5)
            self.selected = 1
        if event.key == pygame.K_6:
            self.scene_manager.kill_scene("boss")
            self.scene_manager.set_scene("boss", {
                "num_players": 2,
                "level": 1,
                "lives": settings.PLAYER_START_LIVES,
            })

        if event.key == pygame.K_2:
            self.start_game(2)
            self.selected = 2
        if self.time > settings.KEY_COOLDOWN and event.key == pygame.K_ESCAPE:
            return "exit"

    def load_markers(self, filename):
        with open(filename, "r") as f:
            lines = f.readlines()
            return [float(i) for i in lines]
