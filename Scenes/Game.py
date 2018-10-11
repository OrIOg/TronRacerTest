from Entities.LightCycle import LightCycle
from Entities.EntityGroup import EntityGroup
import pygame
import colorsys
import time
from math import cos, sin, ceil, radians

def hsv2rgb(h, s, v):
    return tuple(int(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))

def get_length(v1, v2):
    a = (v1[0] - v2[0])**2 + (v1[1] - v2[1])**2
    return a**0.5

def inrange(pos, point, r):
    if get_length(pos, point) <= r:
        return True
    return False

def sum_vector(v1, v2):
    return [v1[0] + v2[0], v1[1] + v2[1]]


def rotate_vector(vec, angle):
    _cos = cos(-radians(angle))
    _sin = sin(-radians(angle))

    result = [(vec[0] * _cos) - (vec[1] * _sin), (vec[0] * _sin) + (vec[1] * _cos)]
    return result

def inrect(pos, topleft, size):
    if pos[0] >= topleft[0] and pos[1] >= topleft[1] and pos[0] <= topleft[0]+size[0] and pos[1] <= topleft[1]+size[1]:
        return True
    return False


def button(screen, pos, textrender, callback=None):
    if textrender is None : return
    text_size = textrender.get_rect().size
    pos = [pos[0], pos[1]]
    pos[0] = pos[0] - text_size[0] * 0.5
    isOn = inrect(pygame.mouse.get_pos(), pos, text_size)

    if isOn:
        textrender = pygame.transform.rotozoom(textrender, sin(time.clock() * 1),
                                                                                0.5 + 0.2 * (cos(time.clock() * 2) + 1))
        if pygame.mouse.get_pressed()[0]:
            callback()
    screen.blit(textrender, pos)


def timer(screen, pos, text, color, callback=None):
    text_size = Scene.font.size(text)
    pos = [pos[0], pos[1]]
    pos[0] = pos[0] - text_size[0] * 0.5

    textrender = Scene.font.render(text, 10, color)

    screen.blit(textrender, pos)


class Scene:
    font = None

    def __init__(self, director, **kwargs):
        if Scene.font is None :
            Scene.font = pygame.font.SysFont("Ubuntu", 150, True)
        self._dir = director
        self.entities = EntityGroup()

        self.light_cycles = kwargs.get("LigthCycles")
        if self.light_cycles is None:
            raise Exception('No key-mapping', 'The programmer is stupid')

        count = len(self.light_cycles)
        screen = director.screen.get_rect()
        max_length = (screen.height if screen.height <= screen.width else screen.width) * 0.5

        for i, lc in enumerate(self.light_cycles):
            pos = sum_vector(screen.center, rotate_vector([20, 0], 180+(i/count)*360))
            angle = (i/count)*360 + 180
            hue = i/count
            self.entities.add(LightCycle(i+1, pos, angle, hue, lc.get("LEFT"), lc.get("RIGHT")))

        # self.entities.add(LightCycle((64, 64), 0, pygame.K_q, pygame.K_d))
        # self.entities.add(LightCycle((512, 512), 0, pygame.K_LEFT, pygame.K_RIGHT))

        self.text = {"Message": None, "Replay": None, "Quit": None}

        self.timer = 3
        self.winner = None
        self.stage = 0

    def update(self, dtime, events):
        if self.stage == 0:
            self.timer -= dtime * 1.5
            if self.timer <= 0:
                self.stage = 10
        elif self.stage == 10:
            self.entities.update(dtime, events)

            to_remove = []
            for lc in self.entities.sprites():
                for lc2 in self.entities.sprites():
                    if lc is not lc2 and inrange(lc.get_forward(), lc2.rect.center, 32):
                        to_remove.append(lc)
                        break
                    for trail_list in lc2.trails:
                        for trail in trail_list:
                            if not lc.phantom and inrange(lc.get_forward(), trail, LightCycle.SIZE):
                                to_remove.append(lc)
                                break

            self.entities.remove(to_remove)

            if len(self.entities) <= 1:
                color = (255, 0, 0)
                message = "Everyone is ded"
                self.stage = 666
                if len(self.entities) == 0:
                    self.winner = None
                else:
                    self.winner = self.entities.sprites()[0]
                    message = "Player {0} win !".format(self.winner.id)
                    color = self.winner.color

                self.text["Message"] = Scene.font.render(message, 10, color)
                self.text["Replay"] = Scene.font.render("Replay", 10, color)
                self.text["Quit"] = Scene.font.render("Quit", 10, color)
        elif self.stage == 666:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN]:
                self.reset()

    def reset(self):
        self._dir.load_scene(Scene(self._dir, LigthCycles=self.light_cycles))
        return

    def quit(self):
        self._dir.stop()

    def draw_menu(self, screen):
        screen.fill((200, 200, 200, 255), None, pygame.BLEND_RGBA_MULT)

        size = screen.get_rect().size

        message = pygame.transform.rotozoom(self.text["Message"], cos(time.clock() * 2) * 1, 1 + 0.2 * (sin(time.clock() * 2)+1))

        button(screen, [size[0]*0.5, size[1]*0.3], self.text["Replay"], self.reset)
        button(screen, [size[0]*0.5, size[1]*0.45], self.text["Quit"], self.quit)

        size = screen.get_rect().size
        x = size[0] * 0.5 - message.get_rect().centerx
        y = size[1] * 0.125
        screen.blit(message, (x, y))

    def draw(self, screen):
        screen.fill((64, 64, 64))

        self.entities.draw(screen)
        if self.stage == 0:
            screen.fill((100, 100, 100, 255), None, pygame.BLEND_RGBA_MULT)
            timer(screen, screen.get_rect().center, "{0}".format(ceil(self.timer)), (255, 255, 255))
        elif self.stage == 666:
            self.draw_menu(screen)

        pygame.display.update()
