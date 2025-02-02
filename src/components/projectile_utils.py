import pygame


def collide_bullets(scene_groups, hit_alien):
    collisions = pygame.sprite.groupcollide(
        scene_groups["aliens"], scene_groups["bullets"], False, True, collided=pygame.sprite.collide_mask
    )

    for alien, bullets in collisions.items():
        for bullet in bullets:
            hit_alien(alien, bullet.player)
            break


def collide_bombs(scene_groups, hit_player):
    collisions = pygame.sprite.groupcollide(
        scene_groups["players"], scene_groups["bombs"], False, True, collided=pygame.sprite.collide_mask
    )

    for player, bombs in collisions.items():
        if bombs and player.stasis <= 0 and not player.dead:
            hit_player(player)
            break
