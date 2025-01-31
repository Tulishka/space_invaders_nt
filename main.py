import pygame

from src import settings
from src.scenes.boss_scene import BossScene
from src.scenes.game_scene import GameScene
from src.scenes.gameover_scene import GameOverScene
from src.scenes.menu_scene import MenuScene
from src.core.scene_manager import SceneManager
from src.scenes.scores_scene import ScoresScene
from src.scenes.trailer_scene import TrailerScene


def main():
    pygame.init()
    pygame.display.set_caption("Space Invaders: Новая угроза")

    pygame.mouse.set_visible(False)
    pygame.mixer_music.set_endevent(settings.MUSIC_END_EVENT)

    scene_manager = SceneManager()
    screen = pygame.display.set_mode(settings.SCREEN_SIZE)

    scene_manager.add_scene("menu", MenuScene)
    scene_manager.add_scene("game", GameScene)
    scene_manager.add_scene("gameover", GameOverScene)
    scene_manager.add_scene("trailer", TrailerScene)
    scene_manager.add_scene("boss", BossScene)
    scene_manager.add_scene("scores", ScoresScene)

    scene_manager.set_scene("menu")

    run = True
    clock = pygame.time.Clock()

    while run:
        dt = clock.get_time() / 1000
        for event in pygame.event.get():
            result = scene_manager.process_event(event)

            if event.type == pygame.QUIT or result == "exit":
                run = False

        scene_manager.update(dt)
        scene_manager.draw(screen)
        pygame.display.update()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
