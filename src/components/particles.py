import pygame
import random
import math
from pygame.sprite import Sprite


class Particle(Sprite):
    """Класс частицы"""

    def __init__(self, sprite_group: pygame.sprite.Group, image: pygame.Surface,
                 pos: tuple[int, int], spd: tuple[float, float], lifetime: float, gravity: float = 98):
        super().__init__(sprite_group)
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
        self.spd *= 0.99
        self.rect.center = self.pos


def create_particle_explosion(
        group: pygame.sprite.Group,
        target: pygame.sprite.Sprite,
        num_particles: int,
        size_range: tuple[int, int],
        initial_spd: int,
        add_spd: tuple[float, float] = (0, 0),
        lifetime_mult: int = 1
):
    """Функция создает частицы из переданного спрайта
    :param group: Группа спрайтов в которую будут добавлены частицы.
    :param target: Спрайт из которого и на месте которого будут созданы частицы.
    :param num_particles: Количество частиц.
    :param size_range: Диапазон размеров частиц.
    :param initial_spd: Начальная скорость разлёта частиц (от центра).
    :param add_spd: Добавочная начальная скорость (добавляется к каждой частице).
    :param lifetime_mult: Множитель времени жизни.
    :return None:
    """
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

        lifetime = random.uniform(0.8, 1.5) * lifetime_mult
        Particle(
            sprite_group=group,
            image=particle_img,
            pos=(rect.left + x, rect.top + y),
            spd=spd,
            lifetime=lifetime,
            gravity=98
        )
