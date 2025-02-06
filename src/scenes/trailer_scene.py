import pygame

from src import settings
from src.core.scene import Scene
from src.core.scene_manager import SceneManager


class TrailerScene(Scene):
    """Сцена возникает перед уровнем"""

    SCENE_TIMEOUT = 3
    SCREEN_MOVE_SPEED = 200

    def __init__(self, scene_manager: SceneManager, params: dict = None):
        super().__init__(scene_manager, params)
        self.back_image = pygame.image.load("img/game_back.jpg")
        self.back_image_top = 0
        self.hidden_height = self.back_image.get_height() - settings.SCREEN_HEIGHT

    def on_show(self, first_time: bool):
        """Обработчик события включения сцены.
        :param first_time: True если сцена появилась первый раз.
        :return None:
        """
        self.time = 0
        if self.params.get("level", 1) == 1:
            self.back_image_top = 0
        else:
            self.back_image_top = settings.SCREEN_HEIGHT - self.back_image.get_height()

    def update_params(self, params: dict):
        """Обновление сцены без её пересоздания"""
        super().update_params(params)
        font_object = pygame.font.Font(None, 42)
        level = params.get("level", 1)
        self.text = font_object.render(f"Уровень {level}", True, "white")

    def update(self, dt):
        """Обновление состояния сцены.
        :param dt: Время с прошлого выполнения этой функции.
        :return None:
        """
        super().update(dt)
        self.back_image_top -= dt * self.SCREEN_MOVE_SPEED
        if abs(self.back_image_top) > self.hidden_height:
            self.back_image_top = -self.hidden_height
        if self.time > self.SCENE_TIMEOUT:
            self.run_game()

    def draw(self, screen: pygame.Surface):
        """Отрисовка сцены.
        :param screen: Поверхность на которой рисовать.
        :return None:
        """
        screen.blit(self.back_image, (0, self.back_image_top))
        screen.blit(self.text, (settings.SCREEN_WIDTH // 2 - self.text.get_width() // 2,
                                settings.SCREEN_HEIGHT // 2 - self.text.get_height() // 2))

    def run_game(self):
        """Запуск игры"""
        self.scene_manager.change_scene("game", self.params)

    def process_event(self, event):
        """Обработка событий pygame
        :param event: Событие pygame
        :return None:
        """
        if event.type != pygame.KEYDOWN or self.time < settings.SCENE_KEY_COOLDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            self.scene_manager.pop_scene()
            return True

        self.run_game()
