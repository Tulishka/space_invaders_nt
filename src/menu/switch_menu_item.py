from typing import Callable

import pygame

from .items_menu import ItemsMenu
from .menu_item import ImageMenuItem


class SwitchMenuItem(ImageMenuItem):
    """Элемент меню для выбора значения из списка"""

    def __init__(self, parent: ItemsMenu, switch_values: list, start_index: int = 0,
                 action: Callable = None, key: int = None,
                 template: str = "{}",
                 changed_callback: Callable[[], None] = None,
                 font_color="green", font_size: int = 32):
        self.switch_values = switch_values
        self.current_index = start_index
        self.start_index = start_index
        self.changed_callback = changed_callback
        self.font_color = font_color
        self.arrow_color = (0, 255, 0)
        self.disabled_color = (40, 40, 40)
        self.font = pygame.font.Font(None, font_size)
        self.template = template
        self.click_width = 25
        self.enabled = True

        initial_image = self.render_image()
        super().__init__(parent, initial_image, action, key)

    def max_text_size(self) -> tuple[int, int]:
        """Измеряет все значения которые могут отображаться в переключателе и возвращает максимальный размер"""
        max_height = max_width = 0
        for text in self.switch_values:
            w, h = self.font.size(text)
            max_height = max(max_height, h)
            max_width = max(max_width, w)
        return max_width, max_height

    def render_image(self) -> pygame.Surface:
        """Отрисовывает изображение переключателя в текущем состоянии"""
        value = self.switch_values[self.current_index]
        text_img = self.font.render(self.template.format(value), True,
                                    self.font_color if self.enabled else self.disabled_color)

        # Активны ли стрелки
        left_arr = self.enabled and self.current_index > 0
        right_arr = self.enabled and self.current_index < len(self.switch_values) - 1

        width = text_img.get_width()
        height = text_img.get_height()
        spacing = 5

        left_arr = self.font.render('<<', True, self.arrow_color if left_arr else self.disabled_color)
        width += left_arr.get_width() + spacing
        self.click_width = left_arr.get_width() + spacing

        right_arr = self.font.render('>>', True, self.arrow_color if right_arr else self.disabled_color)
        width += right_arr.get_width() + spacing

        image = pygame.Surface((width, height), pygame.SRCALPHA)
        xx = 0

        image.blit(left_arr, (xx, 0))
        xx += left_arr.get_width() + spacing

        image.blit(text_img, (xx, 0))
        xx += text_img.get_width() + spacing

        image.blit(right_arr, (xx, 0))

        return image

    def process_event(self, event) -> bool:
        """Обработчик событий переключателя

        Обрабатывает события кнопок клавиатуры и нажатия мыши, что бы управлять
        выбором текущего значения из списка значений.
        Обработка идет, только если это текущий элемент меню и он не отключен.

        :return: Возвращает True если событие было обработано.
        """
        if self.enabled and self.parent.selected is self:
            change = 0
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a) and self.current_index > 0:
                    change = -1
                elif event.key in (pygame.K_RIGHT, pygame.K_d) and self.current_index < len(self.switch_values) - 1:
                    change = 1
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.rect.collidepoint(event.pos):
                    click_x = event.pos[0] - self.rect.left
                    if click_x < self.click_width and self.current_index > 0:
                        change = -1
                    elif click_x > self.click_width and self.current_index < len(self.switch_values) - 1:
                        change = 1
            if change:
                self.current_index += change
                self.update_image()
                if self.changed_callback:
                    self.changed_callback()
                return True

        return super().process_event(event)

    def set_current_index(self, index: int):
        """Метод устанавливает текущее значение переключателя и обновляет отображение.

        :param index: Индекс выбираемого элемента (из self.switch_values)
        :return: None
        """
        self.current_index = max(0, min(index, len(self.switch_values) - 1))
        self.update_image()

    def set_enabled(self, enabled: bool):
        """Метод устанавливает признак переключателя enabled (включен)"""
        if self.enabled != enabled:
            self.enabled = enabled
            self.update_image()

    def update_image(self):
        self.image = self.render_image()
        self.rect.size = self.image.get_size()

    def is_changed(self) -> bool:
        return self.current_index != self.start_index
