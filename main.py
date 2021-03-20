import pygame
#import random 
#import sys
from time import time
from pygame.locals import *

star_img = pygame.image.load('data/obj.png')
planet_img = pygame.image.load('data/plan.png')
hole_img = pygame.image.load('data/sun.png')

class settings:
    def __init__(self, fps=50, size=(1920, 1080), autosize=False):
        self.fps = fps
        if autosize:
            size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        self.size = size
        self.screen = None

class star:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.r = 16
        self.m = 1

class planet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.r = 10
        self.m = 1000

class hole:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.r = 30
        self.m = 1000000

cur_time = int(round(time() * 1000))
cadrs = 0
fps = 0
def fps_val(): # значение кадров/c
    global cur_time, cadrs, fps
    cadrs += 1
    pygame.draw.rect(user.screen, 'black', (0, 0, 30, 80))
    if int(round(time() * 1000)) - cur_time > 1000:
        fps = cadrs
        cadrs = 0
        cur_time = int(round(time() * 1000))
    user.screen.blit(font.render(str(fps) + ' fps', True, (255, 255, 0)), (0, 0))
    user.screen.blit(font.render(str(len(space_objects)) + ' obj', True, (230, 230, 230)), (0, 30))

    user.screen.blit(font.render('[0]: ' + str((int((space_objects[0].x + movement[0]) * zoom), \
        int((space_objects[0].y + movement[1]) * zoom))) + ', Real: ' + str((int(space_objects[0].x), \
        int(space_objects[0].y))), True, (0, 230, 230)), (0, 60))

def step(): # шаг
    for i in range(len(space_objects)): # текущий
        for j in range(len(space_objects)): # второй
            if i == j: 
                continue
            dx = space_objects[j].x - space_objects[i].x
            dy = space_objects[j].y - space_objects[i].y

            r = dx * dx + dy * dy # R^2
            if r < 0.1: 
                r = 0.1 # избегаем деления на очень маленькое число
            a = G * space_objects[j].m / r
            r = r ** 0.5 # R
            if abs(dx) > space_objects[j].r or abs(dy) > space_objects[j].r:
                ax = a * dx / r # a * cos
                ay = a * dy / r # a * sin
                space_objects[i].vx += ax * dt
                space_objects[i].vy += ay * dt
            else:
                ax = a * dx / space_objects[j].r
                ay = (-1) * a * dy / space_objects[j].r
                space_objects[i].vx -= ax * dt
                space_objects[i].vy += ay * dt
    # изменение координат
    for i in range(len(space_objects)):
        space_objects[i].x += space_objects[i].vx * dt
        space_objects[i].y += space_objects[i].vy * dt


if __name__ == '__main__':
    zoom = 1
    moving_right, moving_left, moving_up, moving_down = False, False, False, False

    movement_speed = 4
    movement = [0, 0]

    pygame.init()
    user = settings(autosize=True)
    user.screen = pygame.display.set_mode(user.size, pygame.FULLSCREEN, pygame.OPENGL, vsync=1)
    pygame.display.set_caption('Space_physics')
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)
    G = 100
    speed = 100
    dt = (1/user.fps) * speed # шаг времени для объектов

    space_objects = []
    aStar = star(300, 300)
    space_objects.append(aStar)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_d:
                    moving_right = True
                if event.key == K_a:
                    moving_left = True
                if event.key == K_w:
                    moving_up = True
                if event.key == K_s:
                    moving_down = True
                if event.key == K_ESCAPE:
                    running = False
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4: # вперед
                    zoom += 0.1
                    if movement_speed > 6:
                        movement_speed -= 2
                elif event.button == 5: # назад
                    zoom -= 0.1
                    if zoom <= 0.1:
                        zoom = 0.1
                    movement_speed += 2
                elif event.button == 1:
                    aStar = star(int(event.pos[0] / zoom - movement[0] - 16), int(event.pos[1] / zoom - movement[1] - 16))
                    space_objects.append(aStar)

            if event.type == KEYUP:
                if event.key == K_d:
                    moving_right = False
                if event.key == K_a:
                    moving_left = False
                if event.key == K_w:
                    moving_up = False
                if event.key == K_s:
                    moving_down = False
        if moving_up:
            movement[1] += movement_speed
        if moving_down:
            movement[1] -= movement_speed
        if moving_left:
            movement[0] += movement_speed
        if moving_right:
            movement[0] -= movement_speed  
        display = pygame.Surface((user.size[0], user.size[1]))
        display.fill((0, 0, 0))
        step()
        for i in range(len(space_objects)):
                display.blit(pygame.transform.scale(star_img, (int(star_img.get_width() * zoom), \
                    int(star_img.get_height() * zoom))), (int((space_objects[i].x + movement[0]) * zoom - 16), \
                    int((space_objects[i].y + movement[1]) * zoom - 16)))

        user.screen.blit(display, (0,0))
        fps_val()
        pygame.display.update()
        clock.tick(user.fps)

    pygame.quit()
    exit('Exit')