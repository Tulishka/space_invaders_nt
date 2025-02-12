import random

from src import settings
from src.aliens import SceneAlien
from src.aliens.alien import AlienState
from src.core.animation import update_animations_images
from src.components.projectile import Bomb
from src.core import pg_utils
from src.core.cooldown import Cooldown
from src.core.scene_manager import SceneManager
from src.scenes.gameover_scene import GameOverScene


class DefeatScene(GameOverScene):
    """Класс сцены Поражения"""

    title = "ПОРАЖЕНИЕ"
    title_color = "red"

    def __init__(self, scene_manager: SceneManager, params: dict = None):
        super().__init__(scene_manager, params)
        self.alien_spawn_cd = Cooldown(self, 0.8, 0.4)
        self.alien_shot_cd = Cooldown(self, 0.7, 0.2)

    def on_show(self, first_time: bool):
        """Обработчик события включения сцены.
        :param first_time: True если сцена появилась первый раз.
        :return None:
        """
        super().on_show(first_time)
        self.alien_spawn_cd.start()
        self.alien_shot_cd.start()
        self.scene_groups["bombs"].empty()
        self.scene_groups["aliens"].empty()

    def add_alien(self, y):
        """Добавление пришельца в сцену"""
        alien = SceneAlien(
            self.scene_groups,
            (random.randint(100, settings.SCREEN_WIDTH - 100), y),
            random.choice((1, 2, 3, 7)),
            0,
            (0, random.randint(30, 60))
        )
        for image, set_image in update_animations_images(alien.animations, AlienState.IDLE):
            set_image(pg_utils.darken_image(image, 0.7))

        alien.image = alien.animations[alien.state][0]
        alien.last_shot = 0

    def update(self, dt):
        """Обновление состояния сцены.
        :param dt: Время с прошлого выполнения этой функции.
        :return None:
        """
        super().update(dt)
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
                b = Bomb(alien.rect.midbottom, self.scene_groups["bombs"], alien.type, 0.3)
                b.image = pg_utils.darken_image(b.image, 0.5)
                alien.last_shot = self.time

    def update_params(self, params: dict):
        """Обновление сцены без её пересоздания"""
        self.scene_groups["bombs"].empty()
        self.scene_groups["aliens"].empty()
        super().update_params(params)
