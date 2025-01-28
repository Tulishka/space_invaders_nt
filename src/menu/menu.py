import pygame

from .items_menu import ItemsMenu
from .menu_item import MenuItem
from .. import settings
from ..sound import play_sound


class Menu(ItemsMenu):

    def __init__(self):
        super().__init__()
        self.items: list[MenuItem] = []
        self.time = 0
        self.selected: MenuItem | None = None
        self.selection_extend_x = 25
        self.selection_extend_y = 5
        self.selection_radius = 25
        self.spacing = 20
        self.back_padding = 20
        self.back_image = None
        self.back_rect = None
        self.top = 200
        self.opacity = 200
        self.cursor_image = pygame.image.load('./img/cursor.png')

    def update(self, dt):
        self.time += dt

    def process_event(self, event):

        if event.type == pygame.MOUSEMOTION or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
            mouse_pos = event.pos
            for item in self.items:
                if item.rect.collidepoint(mouse_pos):
                    if item.action:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            item.activate()
                        elif self.selected is not item:
                            item.select()
                    break
            return

        if event.type != pygame.KEYDOWN:
            return

        if event.key in (pygame.K_DOWN, pygame.K_s):
            self.select_next()
        elif event.key in (pygame.K_UP, pygame.K_w):
            self.select_prev()
        elif self.selected and event.key in (pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_RETURN):
            self.selected.activate()
        else:
            for item in self.items:
                if item.process_event(event):
                    break

    def item_activated(self, item: MenuItem):
        self.selected = item

    def item_selected(self, item: MenuItem):
        self.selected = item
        play_sound("menu_beep")

    def select_next(self):
        new = was = self.selected

        if not new:
            idx = 0
        else:
            idx = self.items.index(new) + 1

        for item in self.items[idx:] + self.items[0:idx]:
            new = item
            if item.action:
                break
        else:
            new = was

        if new and new is not was:
            new.select()

    def select_prev(self):
        new = was = self.selected
        if new is None:
            self.select_next()
            return
        idx = self.items.index(new) - 1
        if idx < 0:
            idx = len(self.items) - 1

        for item in [self.items[i] for i in range(idx, -1, -1)] + self.items[-1:idx:-1]:
            new = item
            if item.action:
                break
        else:
            new = was

        if new and new is not was:
            new.select()

    def draw(self, screen: pygame.Surface):
        start_y = settings.SCREEN_HEIGHT // 2 - self.top
        y = start_y
        xc = settings.SCREEN_WIDTH // 2

        if self.back_image:
            screen.blit(self.back_image, self.back_rect)

        max_width = 0
        for item in self.items:
            x = xc - item.get_width() // 2
            item.rect.topleft = x, y
            item.draw(screen)
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
            img.set_alpha(self.opacity)
            self.back_image = img
            self.back_rect = rect

        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[0] != 0 and mouse_pos[1] != 0:
            screen.blit(self.cursor_image, mouse_pos)
