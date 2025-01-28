import pygame

from .items_menu import ItemsMenu
from .menu_item import MenuItem
from .. import settings


class Menu(ItemsMenu):

    def __init__(self):
        super().__init__()
        self.items: list[MenuItem] = []
        self.time = 0
        self.selected: MenuItem | None = None
        self.selection_extend_x = 5
        self.selection_extend_y = 5
        self.selection_radius = 25
        self.spacing = 0
        self.back_padding = 20
        self.back_image = None
        self.back_rect = None

    def update(self, dt):
        self.time += dt

    def process_event(self, event):
        for item in self.items:
            if item.process_event(event):
                break

    def item_activated(self, item: MenuItem):
        pass

    def item_selected(self, item: MenuItem):
        pass

    def draw(self, screen: pygame.Surface):
        start_y = settings.SCREEN_HEIGHT // 2 - 200
        y = start_y
        xc = settings.SCREEN_WIDTH // 2

        if self.back_image:
            screen.blit(self.back_image, self.back_rect)

        max_width = 0
        for item in self.items:
            x = xc - item.get_width() // 2
            item.draw(screen, (x, y))
            max_width = max(max_width, item.get_width())

            if self.selected is item:
                bar_width = self.selected.get_width() + 2 * self.selection_extend_x
                bar_height = self.selected.get_height() + 2 * self.selection_extend_y
                pygame.draw.rect(
                    screen, (0, 200, 0),
                    pygame.Rect(
                        x - self.selection_extend_x,
                        y - self.selection_extend_y,
                        bar_width, bar_height
                    ), 2, self.selection_radius
                )

            y += item.get_height() + self.spacing

        if not self.back_image:
            height = y - start_y + self.back_padding * 2
            width = max_width + self.back_padding * 2

            img = pygame.Surface((width, height), flags=pygame.SRCALPHA)
            rect = img.get_rect(
                center=(xc, start_y + (y - start_y) // 2)
            )
            pygame.draw.rect(img, (10, 10, 20), (0, 0, width, height), 0, 8)
            pygame.draw.rect(img, (40, 40, 80), (0, 0, width, height), 2, 8)
            img.set_alpha(200)
            self.back_image = img
            self.back_rect = rect
