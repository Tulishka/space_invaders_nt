import pygame

import settings
from scene import Scene


class TrailerScene(Scene):
    SCENE_TIMEOUT = 3
    SCREEN_MOVE_SPEED = 200

    def update_params(self, params):
        super().update_params(params)
        font_object = pygame.font.Font(None, 42)
        level = params.get("level", 1)
        self.text = font_object.render(f"Уровень {level}", True, "white")

    def update(self, dt):
        super().update(dt)
        if self.time > self.SCENE_TIMEOUT:
            self.run_game()

    def draw(self, screen):
        screen.fill((0, 0, 0))
        screen.blit(self.text, (settings.SCREEN_WIDTH // 2 - self.text.get_width() // 2,
                                settings.SCREEN_HEIGHT // 2 - self.text.get_height() // 2))

    def run_game(self):
        self.scene_manager.set_scene("game", self.params)

    def process_event(self, event):
        if event.type != pygame.KEYDOWN or self.time < settings.KEY_COOLDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            self.scene_manager.kill_scene("trailer")
            self.scene_manager.set_scene("menu")

        self.run_game()
