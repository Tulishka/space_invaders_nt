from collections import defaultdict

import pygame

from src import settings
from src.components.text_input import InputText
from src.core import db, web_results
from src.core.pg_utils import create_text_sprite
from src.core.scene import Scene
from src.core.scene_manager import SceneManager


class GameOverScene(Scene):
    """Базовый класс финальной сцены"""

    title = "GAME OVER"
    title_color = (255, 255, 255)

    def __init__(self, scene_manager: SceneManager, params: dict = None):

        self.player_names = db.load_player_names()

        self.labels_images = []
        self.num_players = 1
        self.scene_groups = defaultdict(pygame.sprite.Group)

        super().__init__(scene_manager, params)
        self.back_image = pygame.image.load("img/game_back.jpg")
        self.back_image_top = 0
        self.hidden_height = 0
        self.name_input[0].set_focus()
        self.cursor_image = pygame.image.load('./img/cursor.png')

    def on_show(self, first_time: bool):
        """Обработчик события включения сцены.
        :param first_time: True если сцена появилась первый раз.
        :return None:
        """
        self.time = 0
        self.back_image_top = settings.SCREEN_HEIGHT - self.back_image.get_height()

    def update(self, dt):
        """Обновление состояния сцены.
        :param dt: Время с прошлого выполнения этой функции.
        :return None:
        """
        super().update(dt)
        self.back_image_top *= 0.97
        if self.back_image_top > 0:
            self.back_image_top = 0

        for group in self.scene_groups.values():
            group.update(dt)

    def update_params(self, params: dict):
        """Обновление сцены без её пересоздания"""
        super().update_params(params)
        self.num_players = params.get("num_players", 1)

        self.score = self.params.get("score", 0)
        self.scores = [self.params.get(f"p{pnum + 1}_score", 0) for pnum in range(self.num_players)]

        font_title = pygame.font.Font(None, 68)
        font_score = pygame.font.Font(None, 48)
        font_pscore = pygame.font.Font(None, 32)

        text = font_title.render(self.title, True, self.title_color)
        score_img = font_score.render(f"общий счёт: {self.score}", True, "white")
        scores_img = [
            font_pscore.render(f"{pnum + 1}-й игрок: {self.scores[pnum]:0>5}", True, settings.PLAYER_COLORS[pnum])
            for pnum in range(self.num_players)
        ]

        self.labels_images = [(text, 12), (score_img, 12)] + [(pscore, 8) for pscore in scores_img]

        self.scene_groups["labels"].empty()
        self.scene_groups["text"].empty()

        fw = 250
        x = settings.SCREEN_WIDTH // 2 - (fw * self.num_players + (self.num_players - 1) * 20) // 2
        y = settings.SCREEN_HEIGHT - 250
        pos = ((x, y), (x + fw + 20, y))
        self.name_input = []

        for i in range(self.num_players):
            it = InputText(self.scene_groups["text"], pos[i], self.player_names[i], max_length=20,
                           font_color=settings.PLAYER_COLORS[i])
            self.name_input.append(it)
            label = create_text_sprite(self.scene_groups["labels"], f"Введи имя {i + 1}-го игрока")
            label.rect.bottomleft = (it.rect.left + 8, it.rect.top - 5)

        self.name_input[0].set_focus()

    def draw(self, screen: pygame.Surface):
        """Отрисовка сцены.
        :param screen: Поверхность на которой рисовать.
        :return None:
        """
        screen.blit(self.back_image, (0, self.back_image_top))

        for group in self.scene_groups.values():
            group.draw(screen)

        y = 200

        for label, offset in self.labels_images:
            screen.blit(label, (settings.SCREEN_WIDTH // 2 - label.get_width() // 2, y))
            y += label.get_height() + offset

        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[0] != 0 and mouse_pos[1] != 0:
            screen.blit(self.cursor_image, mouse_pos)

    def process_event(self, event):
        """Обработка событий pygame
        :param event: Событие pygame
        :return None:
        """
        for text in self.scene_groups["text"]:
            if text.process_event(event):
                return

        if self.time > settings.SCENE_KEY_COOLDOWN and event.type == pygame.KEYDOWN and event.key in (
                pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN):
            self.save_results()
            self.scene_manager.pop_scene()

    def save_results(self):
        """Сохранение результатов"""
        for i, ti in enumerate(self.name_input):
            self.player_names[i] = ti.value.strip() or f"no_name_{i + 1}"

        db.save_player_names(self.player_names)
        db.add_game_result(
            self.num_players,
            *((self.player_names[idx], self.scores[idx]) for idx in range(self.num_players))
        )
        web_results.send_world_record(
            ", ".join(sorted(self.player_names[:self.num_players])),
            sum(self.scores),
            "👑" if type(self).__name__ == "VictoryScene" else "💀"
        )
