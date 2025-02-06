import pygame

from src import music, settings
from src.aliens import BossAlien
from src.scenes.game_scene import GameScene


class BossScene(GameScene):
    def __init__(self, scene_manager, params):
        super().__init__(scene_manager, params)
        self.music_on = False

        players_start_pos = [
            self.params.get("p1_pos", 100),
            self.params.get("p2_pos", settings.SCREEN_WIDTH - 100),
        ]
        for i, player in enumerate(self.players):
            player.rect.centerx = players_start_pos[i]

    def on_hide(self):
        super().on_hide()

    def create_swarm(self):
        boss = BossAlien(
            self.scene_groups,
            (settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 3)
        )
        boss.time = -4
        return boss

    def swarm_crash_player(self, player):
        return False

    def bonus_ship_should_arrive(self):
        return self.time > 60

    def go_next_level(self):
        music.play("victory")
        self.params["score"] = self.score
        self.params["num_players"] = self.num_players
        self.params["p1_score"] = self.player_score[0]
        self.params["p2_score"] = self.player_score[1]
        self.scene_manager.change_scene("victory", self.params)

    def draw(self, screen):
        if super().draw(screen):
            return True

        if self.swarm.hp > 0 and self.swarm.time > self.swarm.spawn_time + 2:
            bar_width = 50
            bar_height = 5
            x, y = self.swarm.rect.midtop
            y -= 30
            pygame.draw.rect(screen, (100, 0, 0),
                             pygame.Rect(x - bar_width - 5, y - 5, 2 * bar_width + 10, bar_height + 10), 2)
            bar_width *= self.swarm.hp / self.swarm.max_hp
            pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(x - bar_width, y, 2 * bar_width, bar_height))
