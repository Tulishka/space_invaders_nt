from typing import Callable

import pygame

from src.aliens import Alien
from src.components.player import Player


def collide_bullets(scene_groups: dict, hit_alien: Callable[[Alien, Player], None]):
    """Находит столкновения пуль с пришельцами.
    Вызывает колбэк hit_alien, для каждого пришельца в которого попала пуля
    :param scene_groups: Группы спрайтов сцены
    :param hit_alien: функция-колбэк
    :return None:
    """
    collisions = pygame.sprite.groupcollide(
        scene_groups["aliens"], scene_groups["bullets"], False, True, collided=pygame.sprite.collide_mask
    )

    for alien, bullets in collisions.items():
        for bullet in bullets:
            hit_alien(alien, bullet.player)
            break


def collide_bombs(scene_groups: dict, hit_player: Callable[[Alien, Player], None]):
    """Находит столкновения бомб с игроками.
    Вызывает колбэк hit_player, для каждого пришельца в которого попала пуля
    :param scene_groups:
    :param hit_player:
    :return None:
    """
    collisions = pygame.sprite.groupcollide(
        scene_groups["players"], scene_groups["bombs"], False, True, collided=pygame.sprite.collide_mask
    )

    for player, bombs in collisions.items():
        if bombs and player.stasis <= 0 and not player.dead:
            hit_player(player)
            break
