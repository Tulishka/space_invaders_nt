from functools import cache

import pygame


@cache
def load(filename) -> pygame.Surface:
    return pygame.image.load(f"./img/{filename}")
