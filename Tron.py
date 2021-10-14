import pygame
from Scenes import *


class Director:

    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((1920, 1080), pygame.NOFRAME|pygame.DOUBLEBUF)
        self.events = None
        self.scene = None
        self.clock = pygame.time.Clock()
        self.is_running = True

    def stop(self):
        self.is_running = False

    def load_scene(self, scene):
        self.scene = scene
        self.main_loop()

    def main_loop(self):
        while self.is_running:
            if pygame.event.peek(pygame.QUIT):
                pygame.quit()
                exit()
            dtime = self.clock.tick() * 0.001
            self.events = pygame.event.get()
            self.scene.update(dtime, self.events)
            self.scene.draw(self.screen)


if __name__ == "__main__":
    director = Director()
    keymapping = ({"LEFT": pygame.K_q, "RIGHT": pygame.K_d},
                  {"LEFT": pygame.K_LEFT, "RIGHT": pygame.K_RIGHT})
    #keymapping = [{"LEFT": pygame.K_LEFT, "RIGHT": pygame.K_RIGHT} for x in range(666)]
    director.load_scene(Game(director, LigthCycles=keymapping))
