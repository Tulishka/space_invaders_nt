from typing import Callable

import pygame

from .items_menu import ItemsMenu


class MenuItem:
    """Базовый класс для создания пункта меню"""

    def __init__(self, parent: ItemsMenu, action: Callable = None, key: int = None):
        """Конструктор класса
        :param parent: Меню к которому принадлежит создаваемый элемент.
        :param action: Функция, которую необходимо вызвать при активации.
        :param key: Клавиша на которую назначена активация действия.
        """
        self.time = 0
        self.parent = parent
        self.parent.add_item(self)
        self.action = action
        self.key = key
        self.rect = pygame.Rect(0, 0, 1, 1)

    def update(self, dt):
        self.time += dt

    def process_event(self, event) -> bool:
        if event.type == pygame.KEYDOWN and event.key == self.key:
            self.activate()
            return True

        return False

    def get_width(self) -> int:
        return self.rect.width

    def get_height(self) -> int:
        return self.rect.height

    def draw(self, surface):
        pass

    def activate(self):
        """Метод активирует пункт меню"""
        if self.action:
            self.parent.item_activated(self)
            self.action()

    def select(self):
        """Метод выбирает пункт меню"""
        if self.action:
            self.parent.item_selected(self)


class MarginMenuItem(MenuItem):
    """Вид элемента меню для создания отступа между пунктами"""

    def __init__(self, parent: ItemsMenu, y_margin: int):
        super().__init__(parent)
        self.rect.height = y_margin
        self.rect.width = 1


class ImageMenuItem(MenuItem):
    """Элемент меню - картинка"""

    def __init__(self, parent: ItemsMenu, image: pygame.Surface, action: Callable = None, key: int = None):
        super().__init__(parent, action, key)
        self.image = image
        self.rect.width = image.get_width()
        self.rect.height = image.get_height()

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)
