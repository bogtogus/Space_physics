import pygame
import random 
import sys
from pygame.locals import *

star_img = pygame.image.load('desktop/rt/obj.png')
planet_img = pygame.image.load('desktop/rt/plan.png')
hole_img = pygame.image.load('desktop/rt/sun.png')


class settings:
    def __init__(self, fps=60, size='1920x1080', autosize=False):
        self.fps = fps
        if autosize:
            size = str(pygame.display.Info().current_w) + 'x' + str(pygame.display.Info().current_h)
        self.size = list(map(int, size.split('x')))
        self.screen = None

class star:
    def __init__(self, x, y):
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.r = 1
        self.m = 1

class planet:
    def __init__(self, x, y):
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.r = 10
        self.m = 1000

class hole:
    def __init__(self, x, y):
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.r = 30
        self.m = 1000000


# Initialize pygame and create window
zoom = 2

moving_right = False
moving_left = False
moving_up = False
moving_down = False

ctrl_pressed = False
equals_pressed = False
minus_pressed = False
zero_pressed = False

mouvement_speed = 4
movement = [0, 0]

pygame.init()
pygame.mixer.init()
user = settings(autosize=True)
user.screen = pygame.display.set_mode(user.size, pygame.FULLSCREEN)
display = pygame.Surface((int(user.size[0] / zoom), int(user.size[1] / zoom)))
pygame.display.set_caption('Game')
clock = pygame.time.Clock()

space_objects = []
aStar = star(200, 200)
aStar.x = 200
aStar.y = 200
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
            if event.key == K_LCTRL:    
                ctrl_pressed = True
            if event.key == K_EQUALS:
                equals_pressed = True
            if event.key == K_MINUS:
                minus_pressed = True
            if event.key == K_0:
                zero_pressed = True
            if event.key == K_ESCAPE:
                running = False
        if event.type == MOUSEMOTION:
            cursor = event.pos
                
        if event.type == KEYUP:
            if event.key == K_d:
                moving_right = False
            if event.key == K_a:
                moving_left = False
            if event.key == K_w:
                moving_up = False
            if event.key == K_s:
                moving_down = False
            if event.key == K_EQUALS:
                equals_pressed = False
            if event.key == K_MINUS:
                minus_pressed = False
            if event.key == K_0:
                zero_pressed = False
            if event.key == K_LCTRL:    
                ctrl_pressed = False
    if moving_up:
        movement[1] += mouvement_speed
    if moving_down:
        movement[1] -= mouvement_speed
    if moving_left:
        movement[0] += mouvement_speed
    if moving_right:
        movement[0] -= mouvement_speed
    if equals_pressed and ctrl_pressed:
        zoom += 0.1
        print('ZOOMING IN')
    if minus_pressed and ctrl_pressed:
        zoom -= 0.1
        print('ZOOMING OUT')
    if zero_pressed and ctrl_pressed:
        zoom = 1
        print('RESET')
    try:   
        display = pygame.Surface((int(user.size[0] / zoom), int(user.size[1] / zoom)))
    except:
        zoom = 1

    space_objects[0].x = 960/zoom
    space_objects[0].y = 540/zoom
    display.fill((0, 0, 0))
                     
    display.blit(star_img, (space_objects[0].x-8, space_objects[0].y-8))
    #pygame.draw.rect(display,(255, 255, 255),player_rect)
    
    user.screen.blit(pygame.transform.scale(display,user.size), movement)
    pygame.display.update()
    clock.tick(user.fps)

pygame.quit()
exit('Exit -> 01')