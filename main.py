import os
import sys

import pygame

from src import settings
from src.core.db import create_db
from src.core.scene_manager import SceneManager
from src.scenes.boss_scene import BossScene
from src.scenes.defeat_scene import DefeatScene
from src.scenes.game_scene import GameScene
from src.scenes.menu_scene import MenuScene
from src.scenes.scores_scene import ScoresScene
from src.scenes.settings_scene import SettingsScene
from src.scenes.trailer_scene import TrailerScene
from src.scenes.victory_scene import VictoryScene
from src.settings import display_manager

# Получение пути исполняемого файла, что бы сменить текущую папку
# т.к. исполняемый файл может быть запущен в неправильной папке
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(__file__)

os.chdir(application_path)


def main():
    """Инициализация игры и основной игровой цикл"""
    create_db()

    pygame.init()
    pygame.display.set_caption("Space Invaders: Новая угроза")

    display_settings = SettingsScene.load_display_settings()
    if display_settings.get("fullscreen_enabled"):
        # Фикс бага pygame.
        # Так как у нас требуется включить режим полного экрана, создадим простое окно сперва -
        # иначе если сразу создать "полный экран", то pygame больше не сможет менять разрешение
        pygame.display.set_mode(settings.SCREEN_SIZE)

    display_manager.set_mode(**display_settings)

    pygame.mouse.set_visible(False)
    pygame.mixer_music.set_endevent(settings.MUSIC_END_EVENT)

    scene_manager = SceneManager()

    # Регистрация классов сцен
    scene_manager.add_scene_class("menu", MenuScene)
    scene_manager.add_scene_class("game", GameScene)
    scene_manager.add_scene_class("defeat", DefeatScene)
    scene_manager.add_scene_class("victory", VictoryScene)
    scene_manager.add_scene_class("trailer", TrailerScene)
    scene_manager.add_scene_class("boss", BossScene)
    scene_manager.add_scene_class("scores", ScoresScene)
    scene_manager.add_scene_class("settings", SettingsScene)

    # Запуск начальной сцены
    scene_manager.push_scene("menu")

    run = True
    clock = pygame.time.Clock()


    while run:
        dt = clock.get_time() / 1000
        for event in pygame.event.get():
            result = scene_manager.process_event(event)

            if event.type == pygame.QUIT or result == "exit":
                run = False

        scene_manager.update(dt)
        scene_manager.draw(display_manager.screen_surface)

        if pygame.display.is_fullscreen():
            pygame.draw.rect(
                display_manager.screen_surface,
                (100, 100, 200),
                (0, 0, display_manager.screen_surface.get_width(), display_manager.screen_surface.get_height()),
                2
            )

        pygame.display.update()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
