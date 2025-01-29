import pygame
import random
import math
from pygame.sprite import Sprite


class Particle(Sprite):
    def __init__(self, group, image, pos, spd, lifetime, gravity=98):
        super().__init__(group)
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.spd = pygame.Vector2(spd)
        self.pos = pygame.Vector2(pos)
        self.lifetime = lifetime
        self.gravity = gravity
        self.time = 0.0
        self.alpha = 255

    def update(self, dt):
        self.time += dt
        if self.time >= self.lifetime:
            self.kill()
            return

        self.alpha = max(0, int(255 * (1 - self.time / self.lifetime)))
        self.image.set_alpha(self.alpha)

        self.spd.y += self.gravity * dt
        self.pos += self.spd * dt
        self.rect.center = self.pos


def create_particle_explosion(group, target, num_particles, size_range, initial_spd, add_spd=(0, 0), life_time_mult=1):
    image = target.image
    rect = image.get_rect(center=target.rect.center)

    for _ in range(num_particles):
        size = random.randint(*size_range)
        particle_img = pygame.Surface((size, size), pygame.SRCALPHA)

        x = random.randint(0, max(0, rect.width - size))
        y = random.randint(0, max(0, rect.height - size))
        area = pygame.Rect(x, y, size, size)
        particle_img.blit(image, (0, 0), area)

        angle = random.uniform(0, 2 * math.pi)
        speed = initial_spd * random.uniform(0.5, 1.5)
        spd = (
            math.cos(angle) * speed + add_spd[0],
            math.sin(angle) * speed + add_spd[1]
        )

        lifetime = random.uniform(0.8, 1.5) * life_time_mult
        Particle(
            group=group,
            image=particle_img,
            pos=rect.center,
            spd=spd,
            lifetime=lifetime,
            gravity=98
        )
