import pygame
import os
import math
import colorsys
import random

data_folder = os.path.join(os.getcwd(), 'Resources')


def get(*path):
    return os.path.join(data_folder, *path)


def hsv2rgb(h,s,v):
    return tuple(int(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))


def get_length(v1, v2):
    a = (v1[0] - v2[0])**2 + (v1[1] - v2[1])**2
    return a**0.5


def sum_vector(v1, v2):
    return [v1[0] + v2[0], v1[1] + v2[1]]


def inrect(pos, topleft, size):
    if pos[0] >= topleft[0] and pos[1] >= topleft[1] and pos[0] <= topleft[0]+size[0] and pos[1] <= topleft[1]+size[1]:
        return True
    return False

def inscreen(pos, size):
    if pos[0] >= 0 and pos[1] >= 0 and pos[0] <= size[0]-10 and pos[1] <= size[1]-10:
        return True
    return False


def rotate_vector(vec, angle):
    _cos = math.cos(-math.radians(angle))
    _sin = math.sin(-math.radians(angle))

    result = [(vec[0] * _cos) - (vec[1] * _sin), (vec[0] * _sin) + (vec[1] * _cos)]
    return result


class LightCycle(pygame.sprite.Sprite):
    MIN_LENGTH = 5
    MAX_TRAILS = math.inf
    SIZE = 8
    SPEED = 500
    ROTATION = 400

    def __init__(self, id, pos, angle, hue, left, right):
        self.id = id
        pygame.sprite.Sprite.__init__(self)

        self.left_key = left
        self.right_key = right

        self.default_image = pygame.image.load(get('LightCycle.png')).convert_alpha()

        self.color = hsv2rgb(hue, 0.8, 1)
        # add in new RGB values
        self.default_image.fill(self.color + (0,), None, pygame.BLEND_MULT)

        self.image = self.default_image
        self.rect = self.image.get_rect()
        self.real_pos = pos
        self.rect.center = self.real_pos

        self.back_offset = [self.rect.centerx - self.rect.midleft[0], self.rect.centery - self.rect.midleft[1]]

        self.phantom = False
        self.default_velocity = LightCycle.SPEED
        self.angle_rate = LightCycle.ROTATION
        self.velocity = LightCycle.SPEED
        self.angle = angle
        self.trails = [[]]
        self.nb_trails = 0
        # TODO: Add counter for trails to be able to delete them.
        # self.trails_count = 0

        self.image = pygame.transform.rotate(self.default_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        self.last_pos = self.get_back()

    def update_pos(self, dtime):
        xy = (dtime * self.velocity * math.cos(math.radians(-self.angle)), dtime * self.velocity * math.sin(math.radians(-self.angle)))
        self.real_pos = sum_vector(self.real_pos, xy)

        self.rect.center = self.real_pos

    def manage_event(self, events, dtime):
        keys = pygame.key.get_pressed()
        if keys[self.left_key]:
            self.angle += dtime * self.angle_rate
        elif keys[self.right_key]:
            self.angle -= dtime * self.angle_rate

    def get_forward(self):
        result = rotate_vector(self.back_offset, self.angle)
        return [int(self.rect.centerx + result[0]), int(self.rect.centery + result[1])]

    def get_back(self):
        result = rotate_vector(self.back_offset, self.angle)
        return [int(self.rect.centerx - result[0]), int(self.rect.centery - result[1])]

    def update(self, dtime, events):
        self.velocity = self.default_velocity

        self.manage_event(events, dtime)
        self.update_pos(dtime)

        self.image = pygame.transform.rotate(self.default_image, self.angle)
        self.rect = self.image.get_rect(center = self.rect.center)

        size = pygame.display.get_surface().get_rect().size
        new_list = False
        if self.real_pos[0] <= 0:
            new_list = True
            self.real_pos[0] = size[0]
        elif self.get_forward()[0] >= size[0]:
            new_list = True
            self.real_pos[0] = 0

        if self.real_pos[1] <= 0:
            new_list = True
            self.real_pos[1] = size[1]
        elif self.real_pos[1] >= size[1]:
            new_list = True
            self.real_pos[1] = 0

        bb = get_length(self.real_pos, self.last_pos)
        if bb >= LightCycle.MIN_LENGTH:
            self.last_pos = self.get_back()
            empty_list = []
            self.trails[self.nb_trails].append(self.last_pos)

        if new_list:

            end_screen = self.real_pos
            end_screen[0] += dtime * self.velocity * math.cos(math.radians(-self.angle))
            end_screen[1] += dtime * self.velocity * math.sin(math.radians(-self.angle))

            end_screen[0] = max(0, min(end_screen[0], size[0]))
            end_screen[1] = max(0, min(end_screen[1], size[1]))

            self.nb_trails += 1
            empty_list = []
            self.trails.insert(self.nb_trails, empty_list)
        #if not inscreen(self.get_forward(), pygame.display.get_surface().get_rect().size):
        #    self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        self.draw_trails(surface)

    def draw_trails(self, screen):
        for lines in self.trails:
            if len(lines) < 2:
                return
            pygame.draw.aalines(screen, self.color, False, lines)
