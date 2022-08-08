import random

import pygame

from props.particule import Particule


class ParticuleSpawner:
    def __init__(self):
        self.particule_group = pygame.sprite.Group()

    def update(self):
        self.particule_group.update()

    def spawn_particule(self, x, y):
        random_number = random.randrange(20, 40)
        for num_particules in range(random_number):
            new_particule = Particule()
            new_particule.rect.x = x
            new_particule.rect.y = y
            self.particule_group.add(new_particule)
