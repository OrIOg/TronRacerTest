import pygame


class EntityGroup(pygame.sprite.Group):

    def __init__(self):
        pygame.sprite.Group.__init__(self)

    def draw(self, surface):
        sprites = self.sprites()
        for spr in sprites:
            spr.draw(surface)
        self.lostsprites = []

