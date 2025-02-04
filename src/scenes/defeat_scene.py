import random

from src import settings
from src.aliens import SceneAlien
from src.components.projectile import Bomb
from src.core import pg_utils
from src.core.cooldown import Cooldown
from src.scenes.gameover_scene import GameOverScene


class DefeatScene(GameOverScene):
    title = "ПОРАЖЕНИЕ"
    title_color = "red"

    def __init__(self, scene_manager, params=None):
        super().__init__(scene_manager, params)
        self.alien_spawn_cd = Cooldown(self, 0.8, 0.4)
        self.alien_shot_cd = Cooldown(self, 0.7, 0.2)

    def on_show(self, first_time):
        super().on_show(first_time)
        self.alien_spawn_cd.start()
        self.alien_shot_cd.start()
        self.scene_groups["bombs"].empty()
        self.scene_groups["aliens"].empty()

    def add_alien(self, y):
        alien = SceneAlien(
            self.scene_groups,
            (random.randint(100, settings.SCREEN_WIDTH - 100), y),
            random.choice((1, 2, 3, 7)),
            0,
            (0, random.randint(30, 60))
        )
        alien.images = [pg_utils.darken_image(img, 0.7) for img in alien.images]
        alien.image = alien.images[0]
        alien.last_shot = 0

    def update(self, dt):
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

    def update_params(self, params):
        self.scene_groups["bombs"].empty()
        self.scene_groups["aliens"].empty()
        super().update_params(params)
