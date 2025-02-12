import random

import pygame

from src import music, settings
from src.aliens import BonusAlien, Alien
from src.components.particles import create_particle_explosion
from src.components.player import Player
from src.components.projectile_utils import collide_bullets, collide_bombs
from src.aliens.swarm import Swarm
from src.core import images
from src.core.scene import Scene
from src.core.scene_manager import SceneManager
from src.menu import Menu, ImageMenuItem, MarginMenuItem
from src.sound import play_sound, stop_sound


class GameScene(Scene):
    """Класс, который реализует основной игровой процесс - сцену уровня"""

    GAME_OVER_DELAY = 7

    def __init__(self, scene_manager: SceneManager, params: dict):
        """
        :param scene_manager: Менеджер сцен
        :param params: Параметры сцены
        """
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

        self.life_img = images.load("life.png")
        self.back_image = images.load("game_back.jpg")
        self.back_image_top = settings.SCREEN_HEIGHT - self.back_image.get_height()

        self.font_obj = pygame.font.Font(None, 30)
        self.player_score_img = [self.render_score_image(idx) for idx in range(self.num_players)]
        self.current_level_img = self.font_obj.render(f"Ур: {self.level}", True, "yellow")

        self.gameover_time = 0
        self.next_level_time = 0

        self.players = []
        for num in range(self.num_players):
            player = Player(num + 1, self.scene_groups, self.scene_manager, players_start_pos[num])
            self.players.append(player)

        if self.num_players == 1:
            player.alt_keys = settings.PLAYER_KEYS[2]

        # Переменные для отрисовки попадания в игрока (красный экран)
        self.wound = 0
        self.wound_image = None
        self.wound_image_alpha = 0

        self.bonus_ship = False

        self.swarm = self.create_swarm()

        self.menu_opened = False
        self.menu = self.create_menu()
        self.menu_dt_slowing = 0  # Параметр замедления времени, при открытом меню

        # отладка
        self.undead_players = False

    def create_swarm(self):
        """Создает рой
        :return None:
        """
        return Swarm(self.level, self.scene_groups, self.scene_manager)

    def draw(self, screen: pygame.Surface):
        """Отрисовка уровня
        :param screen: Поверхность на которой рисовать
        :return bool:
        """
        screen.blit(self.back_image, (0, self.back_image_top))

        for group in self.scene_groups.values():
            group.draw(screen)

        # отрисовка счета игроков
        sx = (5 + self.player_score_img[0].get_width(), settings.SCREEN_WIDTH - 5)
        for idx in range(self.num_players):
            screen.blit(self.player_score_img[idx], (sx[idx] - self.player_score_img[idx].get_width(), 10))

        screen.blit(self.current_level_img, (settings.SCREEN_WIDTH // 2 - self.current_level_img.get_width() // 2, 10))

        # отрисовка жизней игрока
        x, y = 180, 5
        for i in range(self.lives):
            screen.blit(self.life_img, (x, y))
            x += self.life_img.get_width() + 7

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

    def update_projectiles(self, dt: float):
        """Обновление состояния снарядов
        :param dt: Время с прошлого выполнения этой функции
        :return None:
        """
        self.scene_groups["bombs"].update(dt)
        self.scene_groups["bullets"].update(dt)
        collide_bullets(self.scene_groups, self.hit_alien)
        collide_bombs(self.scene_groups, self.hit_player)

    def swarm_crash_player(self, player: Player):
        """Проверка столкновения роя с игроком
        :param player: игрок
        :return bool:
        """
        return self.swarm.max_y > player.rect.y

    def update_players(self, dt: float):
        """Обновление состояния игроков
        :param dt: Время с прошлого выполнения этой функции
        :return None:
        """
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
            self.scene_manager.change_scene(
                "defeat",
                {
                    "text": "GAME OVER",
                    "num_players": self.num_players,
                    "score": self.score,
                    "p1_score": self.player_score[0],
                    "p2_score": self.player_score[1]
                }
            )

    def hit_player(self, player: Player, minus_lives: int = 1):
        """Обработка получения урона игроком
        :param player: Игрок
        :param minus_lives: Количество потерянных жизней
        :return None:
        """
        if self.undead_players:
            return

        self.wound = 1.0
        self.lives -= minus_lives
        if self.lives > 0:
            player.do_stasis()
        else:
            player.die()

        create_particle_explosion(
            self.scene_groups["particles"],
            player,
            12 * (1 + 2 * player.dead),
            (4, 12),
            60,
            (0, -50)
        )

    def hit_alien(self, alien: Alien, player: Player):
        """Обработка получения урона пришельцем
        :param alien: Пришелец получивший урон
        :param player: Игрок нанёсший урон
        :return None:
        """
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

            if player:
                points = settings.ALIENS_REWARD[alien.type]
                self.score += points
                self.player_score[player.num - 1] += points
                self.player_score_img[player.num - 1] = self.render_score_image(player.num - 1)
                if alien.type == settings.BONUS_ALIEN_TYPE:
                    player.upgrade_gun()

    def bonus_ship_should_arrive(self):
        """Определяет, должен ли появится бонусный пришелец
        :return bool:
        """
        return self.swarm.min_y > settings.SCREEN_HEIGHT // 5

    def update_swarm(self, dt: float):
        """Обновление роя
        :param dt: Время с прошлого выполнения этой функции
        :return None:
        """
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
        """Проверяет условие перехода на следующий уровень
        :return None:
        """
        if self.next_level_time == 0 and len(self.scene_groups["aliens"]) == 0:
            self.next_level_time = self.time + 2
            music.play("next_level")

        if self.gameover_time == 0 and self.next_level_time and self.next_level_time < self.time:
            self.go_next_level()

    def go_next_level(self):
        """Переходит на новый уровень
        :return None:
        """
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
        self.scene_manager.change_scene(next_scene, self.params)

    def update(self, dt: float):
        """Запускает обновление всех составляющих сцены
        :param dt: Время с прошлого выполнения этой функции
        :return:
        """
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
        """Обработка событий
        :param event: pygame событие
        :return None:
        """

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
        elif event.key == pygame.K_PAGEDOWN:
            self.swarm.swarm_down_warp = 100
        elif event.key == pygame.K_BACKSPACE:
            self.undead_players = not self.undead_players
        elif event.key == pygame.K_g:
            for player in self.players:
                player.upgrade_gun()

    def create_menu(self):
        """Создание внутри-игрового меню
        :return Menu:
        """
        menu = Menu()
        font1 = pygame.font.Font(None, 60)
        font3 = pygame.font.Font(None, 40)
        ImageMenuItem(menu, font1.render("ПАУЗА", True, "white"))
        MarginMenuItem(menu, 10)
        menu.selected = ImageMenuItem(menu, font3.render("продолжить", True, "green"), self.close_menu, pygame.K_ESCAPE)
        ImageMenuItem(menu, font3.render("выход", True, "green"), self.game_exit)
        p = p1 = images.load('p1_keys.png')
        if self.num_players > 1:
            p2 = images.load('p2_keys.png')
            p = pygame.Surface((p1.get_width() + p2.get_width() + 30, p1.get_height()), flags=pygame.SRCALPHA)
            p.blit(p1, (0, 0))
            p.blit(p2, (p1.get_width() + 30, 0))
        ImageMenuItem(menu, p)
        menu.back_padding = 40
        menu.selection_extend_x = 15
        menu.opacity = 230
        return menu

    def game_exit(self):
        """Обработчик нажатия кнопки выход
        :return None:
        """
        self.scene_manager.pop_scene()

    def close_menu(self):
        """Обработчик закрытия меню
        :return None:
        """
        self.menu_opened = False
        self.menu_dt_slowing = 0

    def open_menu(self):
        """Обработчик открытия меню
        :return:
        """
        stop_sound()
        play_sound("menu_show")
        self.menu_opened = True
        self.menu_dt_slowing = 1

    def render_score_image(self, player_idx: int):
        """Отрисовка картинки со счётом игрока
        :param player_idx: Индекс игрока
        :return pygame.Surface:
        """
        return self.font_obj.render(
            f"{player_idx + 1}P: {self.player_score[player_idx]}",
            True,
            settings.PLAYER_COLORS[player_idx]
        )
