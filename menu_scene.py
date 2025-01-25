import pygame

import music
import settings
from scene import Scene
from sound import play_sound


class MenuScene(Scene):
    def __init__(self, scene_manager, params=None):
        super().__init__(scene_manager, params)
        font1 = pygame.font.Font(None, 60)
        font2 = pygame.font.Font(None, 28)
        font3 = pygame.font.Font(None, 40)

        p1 = font3.render("1 - игрок", True, "green")
        p2 = font3.render("2 - игрока", True, "green")

        p3 = pygame.Surface(p2.get_size(), flags=pygame.SRCALPHA)
        p3.blit(p1, (0, 0))
        p1 = p3

        self.menu = [
            (font1.render("SPACE INVADERS", True, "white"), 2, 0),
            (font3.render("НОВАЯ УГРОЗА", True, "white"), 50, 0),
            (font2.render("выбери режим", True, "white"), 50, 0),
            (p1, 20, 1),
            (p2, 20, 2),
            (font3.render("рекорды", True, "green"), 20, 3),
        ]
        self.selected = 1
        self.max_select = 3
        self.back_image = pygame.image.load("img/menu_back.jpg")

    def replay_scene(self):
        music.play("menu")
        self.time = 0

    def on_show(self, first_time):
        play_sound("menu_show")
        self.replay_scene()

    def on_hide(self):
        music.stop()

    def draw(self, screen):
        screen.blit(self.back_image, (0, 0))

        start_y = settings.SCREEN_HEIGHT // 2 - 200
        y = start_y

        for item, py, num in self.menu:
            x = settings.SCREEN_WIDTH // 2 - item.get_width() // 2
            screen.blit(item, (x, y))

            if self.selected == num:
                bar_width = 25
                pygame.draw.rect(screen, (0, 200, 0),
                                 pygame.Rect(x - bar_width, y - 5, item.get_width() + 2 * bar_width,
                                             item.get_height() + 10), 2, 25)

            y += item.get_height() + py

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
