from functools import partial

import pygame


class Animation:
    """Класс реализует анимацию спрайтов"""

    def __init__(self, images, fps=2):
        self.images = images
        self.fps = fps

    def get_frame(self, time: float) -> pygame.Surface:
        """Возвращает кадр анимации (surface)

        :param time: время на которое нужно получить кадр анимации,
        :return: pygame.Surface - изображение, кадр анимации
        """
        return self.images[int(time * self.fps) % len(self.images)]

    def set_image(self, index: int, image: pygame.Surface):
        """Обновляет изображение по индексу"""
        self.images[index] = image

    def __getitem__(self, item):
        """Получение изображения по индексу"""
        return self.images[item]


def update_animations_images(animations: dict[str, Animation], name=None):
    """Функция-генератор, перебирает все изображения в словаре анимаций

    Позволяет перебрать все изображения в словаре анимаций и так же обновить их.
    Генератор возвращает изображение и функцию-сеттер с помощью которой можно обновить изображение.

    :param animations: словарь анимаций
    :param name: фильтр по анимации - если нужна конкретная
    :return: None
    """
    for key, animation in animations.items():
        if name is None or key == name:
            for idx, image in enumerate(animation.images):
                yield image, partial(animation.set_image, idx)
