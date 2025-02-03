import pygame
from pygame.sprite import Sprite

from src import settings
from src.components.projectile import Bullet
from src.core.cooldown import Cooldown
from src.core.scene_manager import SceneManager
from src.sound import sounds, play_sound


class Player(Sprite):

    def __init__(self, num: int, scene_groups, scene_manager: SceneManager, start_x: int):
        super().__init__(scene_groups["players"])
        self.scene_groups = scene_groups
        self.num = num
        self.image = pygame.image.load(f'./img/player{self.num}.png')
        self.images = [pygame.image.load(f'./img/player{self.num}.png'), pygame.image.load(f'./img/player_stasis.png')]
        self.kill_image = pygame.image.load(f'./img/player{self.num}k.png')
        self.rect = self.image.get_rect(
            center=(
                start_x,
                settings.SCREEN_HEIGHT - self.image.get_height()
            )
        )
        self.time = 0
        self.spd = settings.PLAYER_SPEED
        self.scene_manager = scene_manager
        self.keys = settings.PLAYER_KEYS[self.num]
        self.alt_keys = settings.PLAYER_KEYS[self.num]
        self.shot_cooldown = Cooldown(self, settings.SHOT_COOLDOWN)
        self.dead = False
        self.stasis = 0
        self.gun_upgraded = 0

        self.sound_shot = sounds[f"player_shot{self.num}"]

    def shot(self):
        self.shot_cooldown.start()
        self.sound_shot.play()
        Bullet(self.rect.midtop, self.scene_groups["bullets"], self)
        if self.gun_upgraded:
            Bullet(self.rect.topleft, self.scene_groups["bullets"], self)
            Bullet(self.rect.topright, self.scene_groups["bullets"], self)

    def update(self, dt):
        self.time += dt

        if self.dead:
            return

        if self.gun_upgraded:
            self.gun_upgraded -= dt
            if self.gun_upgraded < 0:
                self.gun_upgraded = 0

        if self.stasis > 0:
            self.image = self.images[int(self.time * 8) % len(self.images)]
            self.stasis -= dt
        else:
            self.image = self.images[0]

        keys = pygame.key.get_pressed()
        if (keys[self.keys.left] or keys[self.alt_keys.left]) and self.rect.left > 0:
            self.rect.x -= self.spd * dt
        if (keys[self.keys.right] or keys[self.alt_keys.right]) and self.rect.right < settings.SCREEN_WIDTH:
            self.rect.x += self.spd * dt
        if (keys[self.keys.shot] or keys[self.alt_keys.shot]) and self.shot_cooldown():
            self.shot()

    def die(self):
        if not self.dead:
            self.image = self.kill_image
            self.dead = True
            play_sound("player_dead")

    def do_stasis(self):
        self.stasis = settings.PLAYER_STASIS_TIME
        self.gun_upgraded = 0
        play_sound("player_stasis")

    def upgrade_gun(self):
        self.gun_upgraded = settings.PLAYER_UPGRADE_TIME
        play_sound("upgrade_gun")
