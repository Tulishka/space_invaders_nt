import random

from src import settings, sound
from src.aliens import SceneAlien
from src.components.particles import create_particle_explosion
from src.components.projectile import Bullet
from src.components.projectile_utils import collide_bullets
from src.core import pg_utils
from src.core.cooldown import Cooldown
from src.scenes.gameover_scene import GameOverScene


class VictoryScene(GameOverScene):
    title = "ПОБЕДА!"
    title_color = "green"

    def __init__(self, scene_manager, params=None):
        super().__init__(scene_manager, params)
        self.alien_spawn_cd = Cooldown(self, 1.4, 0.5)
        self.shot_cd = Cooldown(self, 1, 0.5)
        self.accurate_shot_cd = Cooldown(self, 0.7, 0.3)
        self.sounds = [sound.load(f"sound/fireworks{n + 1}.wav", 1 if n!=2 else 0.5) for n in range(5)]

    def on_show(self, first_time):
        super().on_show(first_time)
        self.alien_spawn_cd.start()
        self.shot_cd.start()
        self.accurate_shot_cd.start()
        self.scene_groups["aliens"].empty()
        self.scene_groups["bullets"].empty()
        for i in range(4):
            self.add_alien(settings.SCREEN_HEIGHT + random.randint(10, 60))

    def add_alien(self, y):
        alien = SceneAlien(
            self.scene_groups,
            (random.randint(100, settings.SCREEN_WIDTH - 100), y),
            random.choice((1, 2, 3, 7)),
            0,
            (0, -random.randint(60, 120))
        )
        alien.images = [pg_utils.darken_image(img, 0.6) for img in alien.images]
        alien.image = alien.images[0]

    def update(self, dt):
        super().update(dt)
        if self.alien_spawn_cd:
            self.alien_spawn_cd.start()
            self.add_alien(settings.SCREEN_HEIGHT)

        if self.shot_cd:
            self.shot_cd.start()
            x = random.randint(10, settings.SCREEN_WIDTH - 10)
            Bullet((x, settings.SCREEN_HEIGHT), self.scene_groups["bullets"], None)
        elif self.accurate_shot_cd:
            self.accurate_shot_cd.start()
            top_alien = None
            for alien in self.scene_groups["aliens"]:
                if alien.y < settings.SCREEN_HEIGHT // 3 and (not top_alien or alien.y > top_alien.y):
                    top_alien = alien
            if top_alien:
                Bullet((top_alien.rect.centerx, settings.SCREEN_HEIGHT), self.scene_groups["bullets"], None)

        collide_bullets(self.scene_groups, self.hit_alien)

    def hit_alien(self, alien, player=None):
        random.choice(self.sounds).play()
        alien.image = alien.spawn_image
        alien.kill_time = alien.time + 0.1
        create_particle_explosion(
            self.scene_groups["particles"], alien, 24, (2, 5),
            50, (0, -50), 2
        )

    def update_params(self, params):
        self.scene_groups["aliens"].empty()
        super().update_params(params)
