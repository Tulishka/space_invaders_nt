import pygame

import settings
from alien_boss import AlienBoss
from game_scene import GameScene


class BossScene(GameScene):

    def on_hide(self):
        super().on_hide()
        self.scene_manager.kill_scene("boss")

    def create_swarm(self):
        boss = AlienBoss(self.aliens_group,
                         (settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 3),
                         self.players_group, self.bombs_group)
        boss.time = -4
        return boss

    def swarm_crash_player(self, player):
        return False

    def bonus_ship_should_arrive(self):
        return self.time > 60

    def go_next_level(self):
        self.params["score"] = self.score
        self.params["p1_score"] = self.player_score[0]
        self.params["p2_score"] = self.player_score[1]
        self.params["text"] = "VICTORY!"
        self.scene_manager.kill_scene("boss")
        self.scene_manager.set_scene("gameover", self.params)

    def draw(self, screen):
        super().draw(screen)

        if self.swarm.hp > 0:
            bar_width = 50
            bar_height = 5
            x, y = self.swarm.rect.midtop
            y -= 30
            pygame.draw.rect(screen, (100, 0, 0),
                             pygame.Rect(x - bar_width - 5, y - 5, 2 * bar_width + 10, bar_height + 10), 2)
            bar_width *= self.swarm.hp / self.swarm.max_hp
            pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(x - bar_width, y, 2 * bar_width, bar_height))
