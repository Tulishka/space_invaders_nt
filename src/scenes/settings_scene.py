import json
from collections import defaultdict

import pygame

from src.core import images, db
from src.core.pg_utils import create_text_image
from src.core.scene import Scene
from src.core.scene_manager import SceneManager
from src.menu import Menu, ImageMenuItem, MarginMenuItem, SwitchMenuItem
from src.settings import display_manager


class SettingsScene(Scene):
    """Класс сцены меню-настроек"""

    keep_alive = True

    def __init__(self, scene_manager: SceneManager, params: dict = None):
        super().__init__(scene_manager, params)

        resolutions_titles = display_manager.display_modes_titles()

        self.menu = Menu()
        self.menu.spacing = 16
        self.menu.min_width = 280
        ImageMenuItem(self.menu, create_text_image(
            "Настройки", font_size=50, color=(255, 255, 255)
        ))
        MarginMenuItem(self.menu, 4)
        ImageMenuItem(
            self.menu,
            create_text_image("режим отображения:", font_size=28, color="gray")
        )
        if len(resolutions_titles):
            self.mode = SwitchMenuItem(
                self.menu,
                ["в окне", "полный экран"], action=lambda: None,
                font_color="yellow",
                changed_callback=self.select_mode
            )
            self.mode.min_height = self.mode.max_text_size()[1]
            self.menu.selected = self.mode
            MarginMenuItem(self.menu, 4)
            ImageMenuItem(
                self.menu,
                create_text_image("разрешение экрана:", font_size=28, color="gray")
            )
            self.resolution = SwitchMenuItem(self.menu, resolutions_titles, action=lambda: None,
                                             font_color="yellow")
            MarginMenuItem(self.menu, 2)
            ImageMenuItem(
                self.menu,
                create_text_image("применить", font_size=40, color="green"),
                self.apply_display_settings
            )

        else:
            self.mode = None
            self.resolution = None
            ImageMenuItem(
                self.menu,
                create_text_image("дисплей не поддерживается", font_size=26, color="red")
            )

        ImageMenuItem(self.menu, create_text_image(
            "закрыть", font_size=40, color=(200, 200, 255)
        ), self.scene_manager.pop_scene, key=pygame.K_ESCAPE)

        self.scene_groups = defaultdict(pygame.sprite.Group)
        self.back_image = images.load("menu_back.jpg")

    def on_show(self, first_time):
        if self.mode:
            self.mode.set_current_index(int(display_manager.fullscreen_enabled))
            curr = tuple(display_manager.fullscreen_size or (0,0))
            for idx, resolution in enumerate(display_manager.display_modes()):
                if resolution == curr:
                    self.resolution.set_current_index(idx)
                    break
            else:
                self.resolution.set_current_index(0)

            self.resolution.set_enabled(self.mode.current_index == 1)

    def draw(self, screen):
        """Отрисовка сцены.
        :param screen: Поверхность на которой рисовать.
        :return None:
        """
        screen.blit(self.back_image, (0, 0))

        for group in self.scene_groups.values():
            group.draw(screen)

        self.menu.draw(screen)

    def update(self, dt):
        """Обновление состояния сцены.
        :param dt: Время с прошлого выполнения этой функции.
        :return None:
        """
        super().update(dt)
        self.menu.update(dt)

    def process_event(self, event):
        """Обработка событий pygame
        :param event: Событие pygame
        :return None:
        """
        if self.menu.process_event(event):
            return

        super().process_event(event)

    def apply_display_settings(self):
        """Сохраняет и применяет режим дисплея

        :return None:
        """
        display_params = {
            "fullscreen_enabled": self.mode.current_index == 1,
            "fullscreen_size": display_manager.display_modes()[self.resolution.current_index],
        }
        value = json.dumps(display_params)
        db.set_var("display_settings", value)
        print("Настройки дисплея сохранены в БД: ", value)
        display_manager.set_mode(**display_params)

    @staticmethod
    def load_display_settings():
        display_params = {}
        try:
            values = json.loads(db.get_var("display_settings"))
            if isinstance(values, dict):
                display_params = values
        except Exception:
            pass
        print("Настройки дисплея загружены из БД: ", display_params)
        return display_params

    def select_mode(self, current_index: int):
        self.resolution.set_enabled(current_index == 1)
