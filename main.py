import pygame
import random 
import sys
import time
from pygame.locals import *

star_img = pygame.image.load('data/obj.png')
planet_img = pygame.image.load('data/plan.png')
hole_img = pygame.image.load('data/sun.png')

t1 = int(round(time.time() * 1000))
k = 0
fps = 0

class settings:
    def __init__(self, fps=50, size='1920x1080', autosize=False):
        self.fps = fps
        if autosize:
            size = str(pygame.display.Info().current_w) + 'x' + str(pygame.display.Info().current_h)
        self.size = list(map(int, size.split('x')))
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

def fps_val():
    global t1, k, fps
    k += 1
    pygame.draw.rect(user.screen, 'black', (0, 0, 40, 20))
    user.screen.blit(font.render(str(int(fps)), True, (255, 255, 0)), (0, 0))
    if int(round(time.time() * 1000)) - t1 > 1000:
        fps = k
        k = 0
        t1 = int(round(time.time() * 1000))

def step():
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
    # координаты меняем позже, потому что они влияют на вычисление ускорения
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
    user.screen = pygame.display.set_mode(user.size, pygame.FULLSCREEN)
    display = pygame.Surface((int(user.size[0]), int(user.size[1])))
    pygame.display.set_caption('Game')
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)
    G = 100
    speed = 100
    dt = (1/user.fps) * speed

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
                if event.button == 4: #вперед
                    zoom += 0.2
                elif event.button == 5: #назад
                    zoom -= 0.2
                elif event.button == 1:
                    aStar = star((event.pos[0] - movement[0]) / zoom, (event.pos[1] - movement[1]) / zoom)
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
        try:   
            display = pygame.Surface((int(user.size[0] / zoom), int(user.size[1] / zoom)))
        except:
            zoom += 0.1
        step()
        for i in range(len(space_objects)):
            display.blit(star_img, (space_objects[i].x-16, space_objects[i].y-16))

        user.screen.blit(pygame.transform.scale(display,user.size), movement)
        fps_val()
        pygame.display.update()
        clock.tick(user.fps)

    pygame.quit()
    exit('Exit -> 01')