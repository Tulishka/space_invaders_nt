from typing import Callable

import pygame

from .items_menu import ItemsMenu


class MenuItem:
    def __init__(self, parent: ItemsMenu, action: Callable = None, key: int = None):
        self.time = 0
        self.parent = parent
        self.parent.add_item(self)
        self.action = action
        self.key = key

    def update(self, dt):
        self.time += dt

    def process_event(self, event) -> bool:
        if event.type == pygame.KEYDOWN and event.key == self.key:
            self.activate()
            return True

        return False

    def get_width(self) -> int:
        return 0

    def get_height(self) -> int:
        return 0

    def draw(self, surface, pos: tuple[int, int]):
        pass

    def activate(self):
        if self.action:
            self.parent.item_selected(self)
            self.action()
            self.parent.item_activated(self)

    def select(self):
        if self.action:
            self.parent.item_selected(self)


class MarginMenuItem(MenuItem):
    def __init__(self, parent: ItemsMenu, y_margin: int):
        super().__init__(parent)
        self.y_margin = y_margin

    def get_height(self) -> int:
        return self.y_margin


class ImageMenuItem(MenuItem):
    def __init__(self, parent: ItemsMenu, image: pygame.Surface, action: Callable = None, key: int = None):
        super().__init__(parent, action, key)
        self.image = image

    def get_width(self) -> int:
        return self.image.get_width()

    def get_height(self) -> int:
        return self.image.get_height()

    def draw(self, surface, pos: tuple[int, int]):
        surface.blit(self.image, pos)
