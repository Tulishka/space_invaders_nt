from functools import partial

import pygame


class Animation:
    def __init__(self, images, fps=2):
        self.images = images
        self.fps = fps

    def get_frame(self, time: float) -> pygame.Surface:
        return self.images[int(time * self.fps) % len(self.images)]

    def set_image(self, index: int, image: pygame.Surface):
        self.images[index] = image

    def __getitem__(self, item):
        return self.images[item]


def update_animations_images(animations: dict, name=None):
    for key, animation in animations.items():
        if name is None or key == name:
            for idx, image in enumerate(animation.images):
                yield image, partial(animation.set_image, idx)
