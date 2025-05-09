import math
import random
import sys
from collections import defaultdict
from functools import partial

import pygame

from src import music, settings
from src.aliens import SceneAlien
from src.core import images
from src.core.scene import Scene
from src.core.scene_manager import SceneManager
from src.menu import Menu, ImageMenuItem, MarginMenuItem
from src.sound import play_sound


class MenuScene(Scene):
    """Класс сцены меню"""

    keep_alive = True

    def __init__(self, scene_manager: SceneManager, params: dict = None):
        super().__init__(scene_manager, params)
        font3 = pygame.font.Font(None, 40)

        p1 = font3.render("1 - игрок", True, "green")
        p2 = font3.render("2 - игрока", True, "green")

        p3 = pygame.Surface(p2.get_size(), flags=pygame.SRCALPHA)
        p3.blit(p1, (0, 0))
        p1 = p3

        self.menu = Menu()
        ImageMenuItem(self.menu, images.load(f'logo.png'))
        MarginMenuItem(self.menu, 10)
        self.menu.selected = ImageMenuItem(self.menu, p1, partial(self.start_game, 1), pygame.K_1)
        ImageMenuItem(self.menu, p2, partial(self.start_game, 2), pygame.K_2)
        ImageMenuItem(self.menu, font3.render("зал славы", True, "gold"), self.open_results)
        ImageMenuItem(self.menu, font3.render("настройки", True, (200, 200, 255)), self.open_settings)
        ImageMenuItem(self.menu, font3.render("выход", True, (200, 200, 255)), sys.exit)

        self.markers = self.load_markers("music/menu1_markers.txt")
        self.cur_marker = 0
        self.beat_value = 0
        self.scene_groups = defaultdict(pygame.sprite.Group)
        self.bonus_alien_beat_num = 4

        self.scene_groups["aliens"].empty()

        self.back_image = images.load("menu_back.jpg")

    def replay_scene(self):
        """Перезапуск музыки"""
        music.play("menu")
        self.time = 0
        self.cur_marker = 0

    def on_show(self, first_time):
        """Обработчик события включения сцены.
        :param first_time: True если сцена появилась первый раз.
        :return None:
        """
        play_sound("menu_show")

        # для анимации фона
        self.scene_groups["aliens"].empty()

        self.replay_scene()
        self.time = 0

    def on_hide(self):
        """Обработчик закрытия сцены (отключает музыку)"""
        music.stop()

    def draw(self, screen):
        """Отрисовка сцены.
        :param screen: Поверхность на которой рисовать.
        :return None:
        """
        screen.blit(self.back_image, (0, 0))

        for group in self.scene_groups.values():
            group.draw(screen)

        self.menu.selection_extend_x = 25 + 30 * self.beat_value * (self.time > 5)
        self.menu.draw(screen)

    def update(self, dt):
        """Обновление состояния сцены.
        :param dt: Время с прошлого выполнения этой функции.
        :return None:
        """
        super().update(dt)

        self.beat_value *= 0.95 - (0.2 * dt)
        if self.cur_marker < len(self.markers) and self.markers[self.cur_marker] <= self.time:
            self.beat_value = 1
            self.cur_marker += 1
            pos = (settings.SCREEN_WIDTH, int(self.time * 500) % (settings.SCREEN_HEIGHT - 64) + 32)

            if self.bonus_alien_beat_num == self.cur_marker or self.cur_marker % 30 == 0:
                alien_type = settings.BONUS_ALIEN_TYPE
                spd = 200
            else:
                alien_type = random.randint(1, 2)
                spd = random.randint(50, 120)

            SceneAlien(self.scene_groups, pos, alien_type, 0, (-spd, 0 * (1 - pos[1] / settings.SCREEN_HEIGHT)),
                       0.2 * (self.time > 5), random.randint(1000, 2000))

        self.scene_groups["aliens"].update(dt)
        self.menu.update(dt)

    def start_game(self, num_players, level=1):
        """Запускает игру"""
        self.scene_manager.push_scene("trailer", {
            "num_players": num_players,
            "level": level,
            "lives": settings.PLAYER_START_LIVES,
        })
        play_sound("menu_start")

    def process_event(self, event):
        """Обработка событий pygame
        :param event: Событие pygame
        :return None:
        """
        if event.type == settings.MUSIC_END_EVENT:
            self.replay_scene()

        if self.menu.process_event(event):
            return

        if event.type != pygame.KEYDOWN:
            return

        # Кнопки для тестирования и отладки
        if event.key == pygame.K_t:
            self.scene_manager.push_scene("defeat", {
                "num_players": 2,
                "score": 1000,
                "p1_score": 500,
                "p2_score": 500,
                "text": "VICTORY!",
            })
        elif event.key == pygame.K_4:
            self.start_game(1, 4)
        elif event.key == pygame.K_5:
            self.start_game(1, 5)
        elif event.key == pygame.K_6:
            self.scene_manager.push_scene("boss", {
                "num_players": 1,
                "level": 8,
                "lives": settings.PLAYER_START_LIVES,
            })
        elif self.time > settings.SCENE_KEY_COOLDOWN and event.key == pygame.K_ESCAPE:
            return "exit"

    def load_markers(self, filename):
        """Загрузка маркеров для музыки"""
        with open(filename, "r") as f:
            lines = f.readlines()
            return [float(i) for i in lines]

    def open_results(self):
        """Открывает сцену результатов (Зал славы)"""
        play_sound("menu_show")
        self.scene_manager.push_scene("scores", {})

    def open_settings(self):
        """Открывает сцену настроек"""
        play_sound("menu_show")
        self.scene_manager.push_scene("settings", {})
