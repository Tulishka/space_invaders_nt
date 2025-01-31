from collections import defaultdict
from functools import partial

import pygame

from src import settings, music
from src.components.text_input import InputText
from src.core import scores
from src.core.pg_utils import create_text_sprite, create_table, create_text_image
from src.core.scene import Scene
from src.menu import Menu, ImageMenuItem, MarginMenuItem


class ScoresScene(Scene):
    music_theme = "ost_rus"

    def __init__(self, scene_manager, params=None):

        self.scene_groups = defaultdict(pygame.sprite.Group)

        super().__init__(scene_manager, params)
        self.back_image = pygame.image.load("img/game_back.jpg")
        self.back_image_top = 0
        self.hidden_height = 0

        self.cursor_image = pygame.image.load('./img/cursor.png')

        self.scene_groups["table"].empty()
        self.scene_groups["logo"].empty()

        results = scores.get_top_results(10)

        table_width = 400

        tab_rect = pygame.Rect(settings.SCREEN_WIDTH // 2 - table_width // 2, 300,
                               table_width, settings.SCREEN_HEIGHT - 400)

        logo = create_text_sprite(self.scene_groups["logo"], f"SPACE INVADERS", font_size=60, color="yellow")
        logo.rect.center = (settings.SCREEN_WIDTH // 2, 100)

        label = create_text_sprite(self.scene_groups["logo"], f"НОВАЯ УГРОЗА", font_size=40)
        label.rect.midtop = settings.SCREEN_WIDTH // 2, logo.rect.bottom

        text1 = create_text_sprite(self.scene_groups["logo"], f"ТОП-10", font_size=32, color="green")
        text1.rect.midtop = settings.SCREEN_WIDTH // 2, label.rect.bottom + 100

        create_table(results, tab_rect, self.scene_groups["table"])

        self.menu = Menu()
        self.menu.top = settings.SCREEN_HEIGHT - 170
        self.menu.no_back = True
        ImageMenuItem(self.menu, create_text_image("эксклюзивный саундтрек к игре", font_size=26, color="cyan"))
        self.menu.selected = ImageMenuItem(self.menu,
                                           create_text_image("Вторжение пришельцев (rus)", font_size=28, color="green"),
                                           partial(self.set_music_theme, "ost_rus"))
        ImageMenuItem(self.menu, create_text_image("Space Invaders (eng)", font_size=28, color="green"),
                      partial(self.set_music_theme, "ost_eng"))
        ImageMenuItem(self.menu, create_text_image("выход", font_size=28, color="green"), self.exit)

    def on_show(self, first_time):
        music.play(ScoresScene.music_theme, 1, 0)

    def draw(self, screen):
        screen.blit(self.back_image, (0, self.back_image_top))

        for group in self.scene_groups.values():
            group.draw(screen)

        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[0] != 0 and mouse_pos[1] != 0:
            screen.blit(self.cursor_image, mouse_pos)

        self.menu.draw(screen)

    def process_event(self, event):

        if self.menu.process_event(event):
            return

        if self.time > settings.KEY_COOLDOWN and event.type == pygame.KEYDOWN and event.key in (
                pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN):
            self.exit()

    def set_music_theme(self, theme_name):
        ScoresScene.music_theme = theme_name
        self.on_show(0)

    def exit(self):
        self.scene_manager.set_scene("menu")