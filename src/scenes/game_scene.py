import random

import pygame

from src import music, settings
from src.aliens import BonusAlien
from src.components.particles import create_particle_explosion
from src.components.player import Player
from src.core.scene import Scene
from src.menu import Menu, ImageMenuItem, MarginMenuItem
from src.sound import play_sound
from src.components.swarm import Swarm


class GameScene(Scene):
    GAME_OVER_DELAY = 7

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
        self.particles_group = pygame.sprite.Group()

        self.live_img = pygame.image.load("img/life.png")
        self.back_image = pygame.image.load("img/game_back.jpg")
        self.back_image_top = settings.SCREEN_HEIGHT - self.back_image.get_height()

        self.font_obj = pygame.font.Font(None, 30)
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
            player.alt_keys = settings.PLAYER_KEYS[2]

        self.wound = 0
        self.wound_image = None
        self.wound_image_alpha = 0

        self.bonus_ship = False

        self.swarm = self.create_swarm()

        self.menu_opened = False
        self.menu = self.create_menu()
        self.menu_dt_slowing = 0

        # отладка
        self.undead_players = False

    def create_swarm(self):
        return Swarm(self.level, self.aliens_group, self.scene_manager,
                     self.players_group, self.bombs_group)

    def draw(self, screen):
        screen.blit(self.back_image, (0, self.back_image_top))

        self.players_group.draw(screen)
        self.particles_group.draw(screen)
        self.aliens_group.draw(screen)
        self.bombs_group.draw(screen)
        self.bullets_group.draw(screen)

        text = self.font_obj.render(f"{self.score}", True, "white")
        screen.blit(self.text_sch, (5, 10))
        screen.blit(self.text_lvl, (330, 10))
        screen.blit(text, (70, 10))

        x, y = 160, 5
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

        if self.menu_opened:
            self.menu.draw(screen)
            return True

    def update_projectiles(self, dt):
        self.bombs_group.update(dt)
        self.bullets_group.update(dt)

        collisions = pygame.sprite.groupcollide(
            self.aliens_group, self.bullets_group, False, True, collided=pygame.sprite.collide_mask
        )

        for alien, bullets in collisions.items():
            for bullet in bullets:
                if alien.hit():
                    create_particle_explosion(self.particles_group, alien, 12, (2, 6), 40, (0, -30))
                    self.hit_alien(alien, bullet.player)

        collisions = pygame.sprite.groupcollide(
            self.players_group, self.bombs_group, False, True, collided=pygame.sprite.collide_mask
        )

        for player, bombs in collisions.items():
            if bombs and player.stasis <= 0 and not self.undead_players and not player.dead:
                self.hit_player(player)
                create_particle_explosion(
                    self.particles_group,
                    player,
                    12 * (1 + 2 * player.dead),
                    (4, 12),
                    60,
                    (0, -50)
                )

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

            if self.swarm_crash_player(player):
                self.hit_player(player, 1000)
            else:
                count += 1

        if count == 0 and self.gameover_time == 0:
            self.gameover_time = self.time + GameScene.GAME_OVER_DELAY
            music.play("gameover")

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

    def hit_player(self, player, minus_lives=1):
        self.wound = 1.0
        self.lives -= minus_lives
        if self.lives > 0:
            player.do_stasis()
        else:
            player.die()

    def hit_alien(self, alien, player):
        points = settings.ALIENS_REWARD[alien.type]
        self.score += points
        if not player:
            return
        self.player_score[player.num - 1] += points
        if alien.type == settings.BONUS_ALIEN_TYPE:
            player.upgrade_gun()

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
            music.play("next_level")

        if not self.gameover_time and self.next_level_time and self.next_level_time < self.time:
            self.go_next_level()

    def go_next_level(self):
        if self.level + 1 >= len(settings.level):
            next_scene = "boss"
            bonus_for_no_dead = 100 * (self.lives == 3)
            self.lives = min(self.lives + 1, 3)
        else:
            next_scene = "trailer"
            bonus_for_no_dead = 0

        self.params["level"] = self.level + 1
        self.params["score"] = self.score + self.num_players * bonus_for_no_dead
        self.params["p1_score"] = self.player_score[0] + bonus_for_no_dead
        self.params["p2_score"] = self.player_score[1] + bonus_for_no_dead * (self.num_players == 2)

        self.params["p1_pos"] = self.players[0].rect.centerx
        self.params["p2_pos"] = self.players[1 % self.num_players].rect.centerx

        self.params["lives"] = self.lives
        self.scene_manager.kill_scene("game")
        self.scene_manager.kill_scene("boss")
        self.scene_manager.set_scene(next_scene, self.params)

    def update(self, dt):
        if self.menu_opened:
            self.menu.update(dt)
            self.menu_dt_slowing *= 0.95
            if self.menu_dt_slowing < 0.01:
                return
            dt *= self.menu_dt_slowing
        self.time += dt
        if self.gameover_time:
            dt *= max((self.gameover_time - self.time) / GameScene.GAME_OVER_DELAY, 0.1)
        self.update_projectiles(dt)
        self.update_players(dt)
        self.update_swarm(dt)
        self.check_next_level()
        self.particles_group.update(dt)

    def process_event(self, event):

        if self.menu_opened:
            self.menu.process_event(event)
            return

        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            self.open_menu()

        # отладка
        if event.key == pygame.K_DELETE:
            self.aliens_group.empty()
        if event.key == pygame.K_PAGEDOWN:
            self.swarm.swarm_down_warp = 100

        if event.key == pygame.K_BACKSPACE:
            self.undead_players = not self.undead_players

    def create_menu(self):
        menu = Menu()
        font1 = pygame.font.Font(None, 60)
        font3 = pygame.font.Font(None, 40)
        ImageMenuItem(menu, font1.render("ПАУЗА", True, "white"))
        MarginMenuItem(menu, 10)
        menu.selected = ImageMenuItem(menu, font3.render("продолжить", True, "green"), self.close_menu, pygame.K_ESCAPE)
        ImageMenuItem(menu, font3.render("выход", True, "green"), self.game_exit)
        p = p1 = pygame.image.load(f'./img/p1_keys.png')
        if self.num_players > 1:
            p2 = pygame.image.load(f'./img/p2_keys.png')
            p = pygame.Surface((p1.get_width() + p2.get_width() + 30, p1.get_height()), flags=pygame.SRCALPHA)
            p.blit(p1, (0, 0))
            p.blit(p2, (p1.get_width() + 30, 0))
        ImageMenuItem(menu, p)
        menu.back_padding = 40
        menu.selection_extend_x = 15
        menu.opacity = 230
        return menu

    def game_exit(self):
        self.scene_manager.kill_scene("game")
        self.scene_manager.set_scene("menu")

    def close_menu(self):
        self.menu_opened = False
        self.menu_dt_slowing = 0

    def open_menu(self):
        play_sound("menu_show")
        self.menu_opened = True
        self.menu_dt_slowing = 1
