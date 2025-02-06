import pygame
from pygame import BLEND_ALPHA_SDL2


def create_text_image(text, font_size=26, color="white") -> pygame.Surface:
    font_object = pygame.font.Font(None, font_size)
    return font_object.render(text, True, color)


def create_text_sprite(sprite_group, text, pos=(10, 10), font_size=26, color="white") -> pygame.sprite.Sprite:
    sprite = pygame.sprite.Sprite(sprite_group)
    sprite.image = create_text_image(text, font_size, color)
    sprite.rect = sprite.image.get_rect(topleft=pos)
    return sprite


def create_table(
        rows: list[tuple[str, int]],
        rect: pygame.Rect,
        sprite_group,
        spacing=6,
        font_size=28
) -> list:
    top = rect.top
    for idx, (col1, col2, *rem) in enumerate(rows):
        num = create_text_sprite(sprite_group, f"{idx + 1: >3}.", font_size=font_size, color="grey")
        num.rect.topleft = rect.left, top
        val1 = create_text_sprite(sprite_group, f"{col1}", font_size=font_size)
        val1.rect.topleft = num.rect.right + 8, top
        val2 = create_text_sprite(sprite_group, f"{col2}", font_size=font_size)
        val2.rect.topright = rect.right, top
        top += spacing + max(val1.image.get_height(), val2.image.get_height())


def darken_image(image: pygame.Surface, dark_koef: float) -> pygame.Surface:
    image = image.copy()
    image.fill((int(255 * (1 - dark_koef)),) * 3, rect=image.get_rect(), special_flags=pygame.BLEND_MULT)
    return image
