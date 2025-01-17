import pygame

import settings
from scene_manager import SceneManager
from game_scene import GameScene
from menu_scene import MenuScene


def main():
    pygame.init()

    scene_manager = SceneManager()
    screen = pygame.display.set_mode(settings.SCREEN_SIZE)

    scene_manager.add_scene("menu", MenuScene)
    scene_manager.add_scene("game", GameScene)

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
