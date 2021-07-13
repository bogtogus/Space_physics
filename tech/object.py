import pygame
from math import cos, sin, asin, pi, degrees, atan2, radians, ceil, hypot
from global_values import *


class obj:
    def __init__(
            self, x=0.0, y=0.0, 
            img=None, img_name='', 
            r=1.0, m=1.0, vx=0.0, 
            vy=0.0, win_size=(), 
            surface=None):
        self.x = x  # object class stores all physical quantities in the SI system
        self.y = y
        self.r = r
        self.m = m
        self.vx = vx
        self.vy = vy
        self.img = img
        self.win_size = win_size
        self.img_name = img_name
        self.transformed_img = img
        self.surface = surface
        self.coll = False  # collision state (True if collision happened)

    def update(self, zoom=1.0) -> None:
        if self.img_name == 'circle':
            return
        if self.img.get_width() * zoom > 3 and self.img.get_height() * zoom > 3:
            # if the size of the picture on the screen exceeds 3 px
            self.transformed_img = pygame.transform.scale(
                self.img, (int(self.img.get_width() * zoom), 
                           int(self.img.get_height() * zoom)))
        else:
            self.transformed_img = pygame.transform.scale(self.img, (3, 3))

    def draw(
            self,
            zoom=1.0,
            movement=[0, 0],
            mode=False,
            COEFFICIENT=1.0,
            DIST_COEFF=1.0) -> None:
        position_on_display = (
            (self.x * DIST_COEFF + movement[0]) * zoom,
            (self.y * DIST_COEFF + movement[1]) * zoom)
        if position_on_display[0] - self.r * DIST_COEFF * zoom > self.win_size[0] or \
                position_on_display[0] + self.r * DIST_COEFF * zoom < 0 or \
                position_on_display[1] - self.r * DIST_COEFF * zoom > self.win_size[1] or \
                position_on_display[1] + self.r * DIST_COEFF * zoom < 0:
            return  # do not draw objects outside the surface
        if self.img_name == 'circle':
            if self.r * DIST_COEFF * zoom > 2:
                pygame.draw.circle(
                    self.surface, '#777777',
                    (int((self.x * DIST_COEFF + movement[0]) * zoom),
                     int((self.y * DIST_COEFF + movement[1]) * zoom)),
                    self.r * DIST_COEFF * zoom)
            else:
                pygame.draw.circle(
                    self.surface, '#777777',
                    (int((self.x * DIST_COEFF + movement[0]) * zoom),
                     int((self.y * DIST_COEFF + movement[1]) * zoom)), 2)
        else:
            self.surface.blit(
                self.transformed_img, 
                (int((self.x * DIST_COEFF + movement[0]) * zoom -
                     self.transformed_img.get_width() // 2), 
                 int((self.y * DIST_COEFF + movement[1]) * zoom -
                     self.transformed_img.get_height() // 2)))
        if mode:
            # coordinates of the text
            x_coord = ((self.x + self.r) * DIST_COEFF +
                       movement[0]) * zoom
            y_coord = ((self.y + self.r) * DIST_COEFF +
                       movement[1]) * zoom
            if (self.vy != 0 or self.vx != 0):
                sin_dir = self.vy / (hypot(self.vy, self.vx))
                cos_dir = self.vx / (hypot(self.vy, self.vx))
                start = position_on_display  # start point of line
                end = [start[0] + 100 * cos_dir * zoom,
                       start[1] + 100 * sin_dir * zoom]  # end point of line
                rotation = degrees(atan2(start[1] - end[1], end[0] - start[0])) + 90
                pygame.draw.line(self.surface, '#c80000', start, end, 2)  # direction line
                pygame.draw.polygon(
                    self.surface, '#c80000',
                    ((end[0] + (10 * sin(radians(rotation))) * zoom,
                      end[1] + (10 * cos(radians(rotation))) * zoom),
                     (end[0] + (5 * sin(radians(rotation - 120))) * zoom,
                      end[1] + (5 * cos(radians(rotation - 120))) * zoom),
                     (end[0] + (5 * sin(radians(rotation + 120))) * zoom,
                      end[1] + (5 * cos(radians(rotation + 120))) * zoom)))  # arrowhead
            self.surface.blit(
                OBJ_INFO_FONT.render(
                    "vx, vy: {}, {} km/s".format(round(self.vx /1000, 3),
                                                 round(self.vy / 1000, 3)),
                    True, '#c8c8c8'),
                (x_coord, y_coord - 26 * COEFFICIENT))
            self.surface.blit(
                OBJ_INFO_FONT.render(
                    "m: " + str(self.m) + ' kg', True, '#c8c8c8'), 
                (x_coord, y_coord - 10 * COEFFICIENT))
            self.surface.blit(
                OBJ_INFO_FONT.render(
                    "coll: " + str(self.coll), True, '#c8c8c8'), 
                (x_coord, y_coord + 6 * COEFFICIENT))
            self.surface.blit(
                OBJ_INFO_FONT.render(
                    "vx, vy: {}, {} km/s".format(round(self.vx / 1000, 3),
                                                 round(self.vy / 1000, 3)),
                    True, '#c8c8c8'),
                (x_coord, y_coord - 26 * COEFFICIENT))

    def __str__(self) -> str:
        """This function returns information about an object."""
        return "Coordinates: ({}, {}), velocity: ({}, {}), radius: {}, mass: {}".format(
            self.x, self.y, self.vx. self.vy, self.r, self.m)
