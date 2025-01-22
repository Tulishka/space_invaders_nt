import random

import pygame

import settings
from alien import BonusAlien
from sound import play_sound
from player import Player
from scene import Scene
from swarm import Swarm


class GameScene(Scene):
    GAME_OVER_DELAY = 3

    def __init__(self, scene_manager, params):
        super().__init__(scene_manager, params)

        self.lives = self.params.get("lives", settings.PLAYER_START_LIVES)
        self.score = self.params.get("score", 0)
        self.level = self.params.get("level", 1)

        self.player_score = [
            self.params.get("p1_score", 0),
            self.params.get("p2_score", 0),
        ]

        players_start_pos = [100, settings.SCREEN_WIDTH - 100]

        self.bombs_group = pygame.sprite.Group()
        self.bullets_group = pygame.sprite.Group()
        self.players_group = pygame.sprite.Group()
        self.aliens_group = pygame.sprite.Group()

        self.live_img = pygame.image.load("img/life.png")
        self.back_image = pygame.image.load("img/game_back.jpg")
        self.back_image_top = settings.SCREEN_HEIGHT - self.back_image.get_height()

        self.font_obj = pygame.font.SysFont("serif", 24)
        self.text_sch = self.font_obj.render("Очки:", True, "white")
        self.text_lvl = self.font_obj.render(f"Ур: {self.level}", True, "yellow")

        self.time = 0
        self.gameover_time = 0
        self.next_level_time = 0

        self.num_players = self.params.get("num_players", 1)
        self.players = []
        for num in range(self.num_players):
            player = Player(num + 1, self.players_group, self.scene_manager,
                            self.bullets_group, players_start_pos[num])
            self.players.append(player)

        if self.num_players == 1:
            player.alt_keys = Player.PLAYER_KEYS[2]

        self.wound = 0
        self.wound_image = None
        self.wound_image_alpha = 0

        self.bonus_ship = False

        self.swarm = Swarm(self.level, self.aliens_group, self.scene_manager,
                           self.players_group, self.bombs_group)

        # отладка
        self.undead_players = False

    def draw(self, screen):
        screen.blit(self.back_image, (0, self.back_image_top))

        self.players_group.draw(screen)
        self.aliens_group.draw(screen)
        self.bombs_group.draw(screen)
        self.bullets_group.draw(screen)

        text = self.font_obj.render(f"{self.score}", True, "white")
        screen.blit(self.text_sch, (5, 5))
        screen.blit(self.text_lvl, (330, 5))
        screen.blit(text, (70, 5))

        x, y = 150, 5
        for i in range(self.lives):
            screen.blit(self.live_img, (x, y))
            x += self.live_img.get_width() + 7

        if self.wound:
            new_alpha = round(self.wound * 200)

            if not self.wound_image or abs(self.wound_image_alpha - new_alpha) > 10:
                self.wound_image_alpha = new_alpha
                w, h = screen.get_width(), screen.get_height()
                self.wound_image = pygame.Surface((w, h), flags=pygame.SRCALPHA)
                pygame.draw.rect(self.wound_image, (255, 0, 0, new_alpha),
                                 (0, 0, w, h), 0)
            screen.blit(self.wound_image, (0, 0))

    def update_projectiles(self, dt):
        for bomb in self.bombs_group:
            bomb.rect.y += bomb.spd * dt
            if bomb.rect.y > settings.SCREEN_HEIGHT:
                bomb.kill()

        for bullet in self.bullets_group:
            bullet.rect.y += bullet.spd * dt
            if bullet.rect.y < 0:
                bullet.kill()

            alien = pygame.sprite.spritecollideany(
                bullet, self.aliens_group, collided=pygame.sprite.collide_mask)

            if alien:
                bullet.kill()
                if alien.hit():
                    points = settings.ALIENS_REWARD[alien.type]
                    self.score += points
                    self.player_score[bullet.player.num - 1] += points
                    if alien.type == settings.BONUS_ALIEN_TYPE:
                        bullet.player.upgrade_gun()

    def swarm_crash_player(self, player):
        return self.swarm.max_y > player.rect.y

    def update_players(self, dt):
        count = 0
        self.players_group.update(dt)

        if self.wound:
            self.wound *= 0.92
            if self.wound < 0.05:
                self.wound = 0

        for player in self.players_group:
            if player.dead:
                continue

            die = 0

            if self.swarm_crash_player(player):
                die = 1000
            else:
                count += 1

                bullet = pygame.sprite.spritecollideany(
                    player, self.bombs_group, collided=pygame.sprite.collide_mask
                )

                if bullet:
                    bullet.kill()
                    die = player.stasis <= 0 and not self.undead_players

            if die:
                self.wound = 1.0
                self.lives -= die
                if self.lives > 0:
                    player.do_stasis()
                else:
                    player.die()

        if count == 0 and self.gameover_time == 0:
            self.gameover_time = self.time + GameScene.GAME_OVER_DELAY

        if self.gameover_time and self.gameover_time < self.time:
            self.scene_manager.set_scene(
                "gameover",
                {
                    "text": "GAME OVER",
                    "score": self.score,
                    "p1_score": self.player_score[0],
                    "p2_score": self.player_score[1]
                }
            )

    def bonus_ship_should_arrive(self):
        return self.swarm.min_y > settings.SCREEN_HEIGHT // 5

    def update_swarm(self, dt):
        self.swarm.update(dt)

        if not self.bonus_ship and self.bonus_ship_should_arrive():
            self.bonus_ship = True
            x = random.choice((-100, settings.SCREEN_WIDTH + 100))
            spd = settings.BONUS_ALIEN_SPEED * (1 if x < 0 else -1)
            ba = BonusAlien(
                (x, 80),
                spd,
                self.aliens_group,
                self.bombs_group,
                settings.SCREEN_WIDTH + 100 if x < 0 else -100,
            )
            ba.warp_y = 0
            play_sound(f"bonus_alien_{'lr' if spd > 0 else 'rl'}")

    def check_next_level(self):
        if self.next_level_time == 0 and len(self.aliens_group) == 0:
            self.next_level_time = self.time + 2

        if not self.gameover_time and self.next_level_time and self.next_level_time < self.time:
            self.go_next_level()

    def go_next_level(self):
        if self.level + 1 >= len(settings.level):
            # сделать переход на уровень с босом
            next_scene = "menu"
            self.params = {}
        else:
            next_scene = "trailer"
            bonus_for_no_dead = 0
            self.params["level"] = self.level + 1
            self.params["score"] = self.score + self.num_players * bonus_for_no_dead
            self.params["p1_score"] = self.player_score[0] + bonus_for_no_dead
            self.params["p2_score"] = self.player_score[1] + bonus_for_no_dead * (self.num_players == 2)
            self.params["lives"] = self.lives

        self.scene_manager.kill_scene("game")
        self.scene_manager.set_scene(next_scene, self.params)

    def update(self, dt):
        self.time += dt
        self.update_projectiles(dt)
        self.update_players(dt)
        self.update_swarm(dt)
        self.check_next_level()

    def process_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            self.scene_manager.kill_scene("game")
            self.scene_manager.set_scene("menu")

        # отладка
        if event.key == pygame.K_DELETE:
            self.aliens_group.empty()
        if event.key == pygame.K_PAGEDOWN:
            self.swarm.swarm_down_warp = 100

        if event.key == pygame.K_BACKSPACE:
            self.undead_players = not self.undead_players
