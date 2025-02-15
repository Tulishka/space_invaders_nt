import string

import pygame


class InputText(pygame.sprite.Sprite):
    """Класс реализует текстовое поле ввода"""

    active_input = None

    def __init__(self, sprite_group, pos, value="", width=250, height=60, bg_color=(10, 20, 40),
                 border_color=(20, 40, 80),
                 max_length=20, cursor_width=6,
                 cursor_color=(255, 255, 255), font_size=28, font_color=(255, 255, 255)):
        super().__init__(sprite_group)
        self.font_color = font_color
        self.sprite_group = sprite_group
        self.value = value
        self.max_length = max_length
        self.has_focus = False

        self.cursor_width = cursor_width
        self.cursor_color = cursor_color
        self.blink_interval = 0.25
        self.cursor_visible = True
        self.cursor_timer = 0.0

        self.font = pygame.font.Font(None, font_size)
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_radius = 8

        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=pos)

        self.on_change = None
        self.allowed_chars = (
            string.ascii_letters +
            string.digits +
            "_@.!- йцукенгшщзхъфывапролджэячсмитьбюёЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮЁ"
        )
        self.render_image()

    def set_focus(self):
        """Устанавливает фокус ввода на это текстовое поле"""
        if InputText.active_input:
            InputText.active_input.has_focus = False
            InputText.active_input.render_image()

        InputText.active_input = self
        self.has_focus = True
        self.cursor_visible = True
        self.cursor_timer = 0.0
        self.render_image()

    def process_event(self, event) -> bool:
        """Обработчик события

        :param event: событие pygame
        :return bool: True - если событие обработано
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.set_focus()
                return True
            elif self.has_focus:
                self.blur()
        elif self.has_focus and event.type == pygame.KEYDOWN:
            value = self.value
            if event.key == pygame.K_ESCAPE:
                self.blur()
            elif event.key in (pygame.K_RETURN, pygame.K_DOWN, pygame.K_KP_ENTER) or (
                    event.key == pygame.K_TAB and not event.mod & pygame.KMOD_SHIFT):
                return self.next_focus()
            elif event.key == pygame.K_UP or (event.key == pygame.K_TAB and event.mod & pygame.KMOD_SHIFT):
                self.prev_focus()
            elif event.key == pygame.K_BACKSPACE:
                self.set_value(value[:-1])
            else:
                char = event.unicode
                if char in self.allowed_chars:
                    value += char
                if char and len(value) < self.max_length:
                    self.set_value(value)
            return True
        return False

    def set_value(self, value: str, emit_on_change=False):
        """Задает новое значение текстовому полю

        :param value: новое значение
        :param emit_on_change: флаг - вызывать обработчик (колбек) при измении
        :return None:
        """
        if self.value != value:
            self.value = value
            self.render_image()
            if emit_on_change and self.on_change:
                self.on_change()

    def update(self, dt):
        """Обновление состояния текстового поля

        Мигание курсором
        :param dt: время, сек
        :return None:
        """
        if self.has_focus:
            self.cursor_timer += dt
            if self.cursor_timer >= self.blink_interval:
                self.cursor_timer = 0.0
                self.cursor_visible = not self.cursor_visible
                self.render_image()

    def render_image(self):
        """Функция отрисовывает поле в image"""
        self.image.fill((0, 0, 0, 0))
        pygame.draw.rect(
            self.image, self.bg_color,
            self.image.get_rect(),
            border_radius=self.border_radius
        )
        pygame.draw.rect(
            self.image, (self.border_color[0] * 2, self.border_color[1] * 2,
                         self.border_color[2] * 2) if self.has_focus else self.border_color,
            self.image.get_rect(),
            width=2,
            border_radius=self.border_radius
        )

        text_img = self.font.render(self.value, True, self.font_color)
        text_rect = text_img.get_rect(midleft=(10, self.rect.height // 2))

        self.image.blit(text_img, text_rect)

        if self.has_focus and self.cursor_visible:
            cursor_x = text_rect.right + 4 if self.value else 10
            cursor_y = text_rect.centery - text_rect.height // 2
            pygame.draw.line(
                self.image, self.cursor_color,
                (cursor_x, cursor_y + 2),
                (cursor_x, cursor_y + text_rect.height - 2),
                self.cursor_width
            )

    def blur(self):
        """Снять фокус ввода с поля"""
        self.has_focus = False
        InputText.active_input = None
        self.render_image()

    def next_focus(self):
        """Фокус на следующее поле ввода"""
        inputs = list(self.sprite_group)
        idx = inputs.index(self) + 1
        if idx >= len(inputs):
            self.blur()
            return False

        inputs[idx].set_focus()
        return True

    def prev_focus(self):
        """Фокус на предыдущее поле ввода"""
        inputs = list(self.sprite_group)
        idx = inputs.index(self) - 1
        if idx >= 0:
            inputs[idx].set_focus()
