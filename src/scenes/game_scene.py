import random

import pygame

from src import music, settings
from src.aliens import BonusAlien
from src.components.particles import create_particle_explosion
from src.components.player import Player
from src.components.swarm import Swarm
from src.core.scene import Scene
from src.menu import Menu, ImageMenuItem, MarginMenuItem
from src.sound import play_sound, stop_sound


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

        # порядок отрисовки:
        self.scene_groups = {
            "players": pygame.sprite.Group(),
            "aliens": pygame.sprite.Group(),
            "particles": pygame.sprite.Group(),
            "bombs": pygame.sprite.Group(),
            "bullets": pygame.sprite.Group(),
            "shields": pygame.sprite.Group(),
        }

        self.num_players = self.params.get("num_players", 1)

        self.live_img = pygame.image.load("img/life.png")
        self.back_image = pygame.image.load("img/game_back.jpg")
        self.back_image_top = settings.SCREEN_HEIGHT - self.back_image.get_height()

        self.font_obj = pygame.font.Font(None, 30)
        self.text_score = [self.render_score_text(idx) for idx in range(self.num_players)]
        self.text_lvl = self.font_obj.render(f"Ур: {self.level}", True, "yellow")

        self.time = 0
        self.gameover_time = 0
        self.next_level_time = 0

        self.players = []
        for num in range(self.num_players):
            player = Player(num + 1, self.scene_groups, self.scene_manager, players_start_pos[num])
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

    def on_kill(self):
        stop_sound()

    def create_swarm(self):
        return Swarm(self.level, self.scene_groups, self.scene_manager)

    def draw(self, screen):
        screen.blit(self.back_image, (0, self.back_image_top))

        for group in self.scene_groups.values():
            group.draw(screen)

        sx = (5 + self.text_score[0].get_width(), settings.SCREEN_WIDTH - 5)
        for idx in range(self.num_players):
            screen.blit(self.text_score[idx], (sx[idx] - self.text_score[idx].get_width(), 10))

        screen.blit(self.text_lvl, (settings.SCREEN_WIDTH // 2 - self.text_lvl.get_width() // 2, 10))

        x, y = 180, 5
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
        self.scene_groups["bombs"].update(dt)
        self.scene_groups["bullets"].update(dt)

        collisions = pygame.sprite.groupcollide(
            self.scene_groups["aliens"], self.scene_groups["bullets"], False, True, collided=pygame.sprite.collide_mask
        )

        for alien, bullets in collisions.items():
            for bullet in bullets:
                if alien.hit():
                    if alien.is_dead():
                        particles = settings.PARTICLES_KILL_COUNT.get(type(alien).__name__, 12)
                        size = settings.PARTICLES_KILL_SIZE.get(type(alien).__name__, (2, 6))
                    else:
                        particles, size = settings.PARTICLES_HIT_COUNT, settings.PARTICLES_HIT_SIZE

                    create_particle_explosion(
                        self.scene_groups["particles"], alien, particles, size,
                        40, (0, -30),
                        2 if alien.type == settings.BONUS_ALIEN_TYPE else 1
                    )
                    self.hit_alien(alien, bullet.player)

        collisions = pygame.sprite.groupcollide(
            self.scene_groups["players"], self.scene_groups["bombs"], False, True, collided=pygame.sprite.collide_mask
        )

        for player, bombs in collisions.items():
            if bombs and player.stasis <= 0 and not self.undead_players and not player.dead:
                self.hit_player(player)
                create_particle_explosion(
                    self.scene_groups["particles"],
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
        self.scene_groups["players"].update(dt)

        if self.wound:
            self.wound *= 0.92
            if self.wound < 0.05:
                self.wound = 0

        for player in self.scene_groups["players"]:
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
        self.text_score[player.num - 1] = self.render_score_text(player.num - 1)
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
                self.scene_groups,
                settings.SCREEN_WIDTH + 100 if x < 0 else -100,
            )
            ba.warp_y = 0
            play_sound(f"bonus_alien_{'lr' if spd > 0 else 'rl'}")

    def check_next_level(self):
        if self.next_level_time == 0 and len(self.scene_groups["aliens"]) == 0:
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
        self.scene_groups["particles"].update(dt)

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
            self.scene_groups["aliens"].empty()
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
        stop_sound()
        play_sound("menu_show")
        self.menu_opened = True
        self.menu_dt_slowing = 1

    def render_score_text(self, player_idx):
        return self.font_obj.render(
            f"{player_idx + 1}P: {self.player_score[player_idx]}",
            True,
            settings.PLAYER_COLORS[player_idx]
        )
