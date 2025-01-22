import pygame

import settings
from scene import Scene


class GameOverScene(Scene):

    def __init__(self, scene_manager, params=None):
        super().__init__(scene_manager, params)
        self.back_image = pygame.image.load("img/game_back.jpg")

    def on_show(self, first_time):
        self.scene_manager.kill_scene("game")
        self.time = 0

    def update_params(self, params):
        super().update_params(params)
        score = self.params.get("score", 0)
        score1 = self.params.get("p1_score", 0)
        score2 = self.params.get("p2_score", 0)

        font_object = pygame.font.Font(None, 68)
        self.text = font_object.render(self.params.get("text", "GAME OVER"), True, "white")

        font_object = pygame.font.Font(None, 48)
        font_object2 = pygame.font.Font(None, 32)
        self.score = font_object.render(f"общий счёт: {score}", True, "white")
        self.score1 = font_object2.render(f"1-й игрок: {score1}", True, "green")
        self.score2 = font_object2.render(f"2-й игрок: {score2}", True, "green")

    def draw(self, screen):
        screen.blit(self.back_image, (0, 0))

        screen.blit(self.text, (settings.SCREEN_WIDTH // 2 - self.text.get_width() // 2,
                                settings.SCREEN_HEIGHT // 2 - self.text.get_height()))

        y = settings.SCREEN_HEIGHT // 2 + self.text.get_height()

        screen.blit(self.score, (settings.SCREEN_WIDTH // 2 - self.score.get_width() // 2, y))

        y += self.score.get_height() + 8

        screen.blit(self.score1, (settings.SCREEN_WIDTH // 2 - self.score1.get_width() // 2, y))

        if self.params.get("p2_score", 0) > 0:
            y += self.score1.get_height() + 8
            screen.blit(self.score2, (settings.SCREEN_WIDTH // 2 - self.score2.get_width() // 2, y))

    def process_event(self, event):
        if self.time > settings.KEY_COOLDOWN and event.type == pygame.KEYDOWN:
            self.scene_manager.set_scene("menu")
