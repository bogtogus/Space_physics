import pygame
from time import time, sleep
from pygame.locals import *
from math import cos, sin, asin, pi, sqrt


class settings:
    def __init__(self, fps=50, size=(1920, 1080), autosize=False):
        self.fps = fps
        if autosize:
            size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        self.size = size
        self.screen = None


pygame.init()
user = settings(autosize=True)
user.screen = pygame.display.set_mode(user.size, pygame.FULLSCREEN)
pygame.draw.rect(user.screen, '#005ffe', pygame.Rect(480, 490, 960 * 0.1, 50))
font = pygame.font.Font('data/Anonymous Pro B.ttf', 25)
post_font = pygame.font.Font('data/Anonymous Pro B.ttf', 16)
dwnld_text1 = font.render("'W', 'A', 'S', 'D' - движение | Колёсико мыши - масштаб | P - пауза", True, (200, 200, 200))
dwnld_text2 = font.render("E - расширенный режим | 0 - сброс", True, (200, 200, 200))
user.screen.blit(dwnld_text1, (user.size[0] // 2 - dwnld_text1.get_rect().width // 2, 550))
user.screen.blit(dwnld_text2, (user.size[0] // 2 - dwnld_text2.get_rect().width // 2, 580))
pygame.display.update()


class obj:
    def __init__(self, x, y, img, r, m, vx = 0, vy = 0):
        self.x = x
        self.y = y
        self.r = r
        self.m = m
        self.img = img
        self.vx = 0
        self.vy = 0
        self.switch = 1 # состояние столкновения (0)
    def draw(self, zoom, mode: bool):
        if (self.vy != 0 or self.vx != 0) and mode:
            sin = self.vy / ((self.vy * self.vy + self.vx * self.vx) ** 0.5)
            cos = self.vx / ((self.vy * self.vy + self.vx * self.vx) ** 0.5)
            x_coord = (self.x + movement[0] + 10 + self.r) * zoom
            y_coord = (self.y + movement[1] - self.r) * zoom
            pygame.draw.line(display, (200, 0, 0), [(self.x + movement[0]) * zoom, (self.y + movement[1]) * zoom], [(self.x + movement[0] + 100 * cos) * zoom, (self.y + movement[1] + 100 * sin) * zoom], 2)
            display.blit(post_font.render("vx, vy: " + str(round(self.vx, 3)) + ', ' + str(round(self.vy, 3)), True, (200, 200, 200)), (x_coord, y_coord - 26))
            display.blit(post_font.render("m: " + str(self.m), True, (200, 200, 200)), (x_coord, y_coord - 10))
            display.blit(post_font.render("cond: " + str(self.switch), True, (200, 200, 200)), (x_coord, y_coord + 6))
        display.blit(pygame.transform.scale(self.img, (int(self.img.get_width() * zoom), \
            int(self.img.get_height() * zoom))), \
            # x:
            (int((self.x + movement[0] - self.r) * zoom), \
            # y:
            int((self.y + movement[1] - self.r) * zoom)))


def simulation(mass: list, name: str):
    with open('simulations/' + name + '.txt', 'r') as doc:
        sim = doc.readlines()
        sim = list(map(lambda x: x.split(), sim))
        for i in range(len(sim)):
            if len(sim[i]) != 5 and len(sim[i]) != 7:
                continue
            aStar = obj(float(sim[i][0]), float(sim[i][1]), globals()[sim[i][2]], float(sim[i][3]), float(sim[i][4]))
            if len(sim[i]) > 5: #vx, vy
                aStar.vx = float(sim[i][5])
                aStar.vy = float(sim[i][6])
            mass.append(aStar)
        return mass


cur_time = int(round(time() * 1000))
cadrs = 0
fps = 0
def fps_val(): # значение кадров/c
    global cur_time, cadrs, fps
    if int(round(time() * 1000)) - cur_time > 1000:
        fps = cadrs
        cadrs = 0
        cur_time = int(round(time() * 1000))
    data = '{} fps, {} obj, zoom: {}, [end]: {}, Real: {}'.format(str(fps), str(len(space_objects)), str(zoom), \
        str((int((space_objects[-1].x + movement[0]) * zoom), int((space_objects[-1].y + movement[1]) * zoom))), \
        str((int(space_objects[-1].x), int(space_objects[-1].y))))
    user.screen.blit(font.render(data, True, (200, 200, 200)), (0, 0))
    cadrs += 1


def step(): # шаг
    for i in range(len(space_objects)): # текущий
        r_i = space_objects[i].r
        x_i = space_objects[i].x
        y_i = space_objects[i].y
        for j in range(len(space_objects)): # второй
            if i == j: continue
            dx = space_objects[j].x - x_i
            dy = space_objects[j].y - y_i
            r = dx * dx + dy * dy # R^2
            r_j = space_objects[j].r
            if r > (r_j + r_i) * (r_j + r_i):
                a = G * space_objects[j].m / r
                r = sqrt(r) # R
                if r < 0.1: r = 0.1
                ax = a * dx / r # a * cos
                ay = a * dy / r # a * sin
                space_objects[i].vx += ax * dt
                space_objects[i].vy += ay * dt
            else:
                if space_objects[i].switch and space_objects[j].switch:
                    r = sqrt(r)
                    v_x1 = space_objects[i].vx
                    v_y1 = space_objects[i].vy
                    v1 = sqrt(v_x1 * v_x1 + v_y1 * v_y1)
                    m1 = space_objects[i].m
                    
                    v_x2 = space_objects[j].vx
                    v_y2 = space_objects[j].vy
                    v2 = sqrt(v_x2 * v_x2 + v_y2 * v_y2)
                    m2 = space_objects[j].m
                    if v1:
                        F1 = asin(v_y1 / v1)
                    else:
                        F1 = asin(0)
                    if v2:
                        F2 = asin(v_y2 / v2)
                    else:
                        F2 = asin(0)
                    f = asin(dy / r)
                    space_objects[i].vx = ((v1 * cos(F1 - f) * (m1 - m2) + 2 * m2 * v2 * cos(F2 - f)) * cos(f)) \
                        / (m1 + m2) + v1 * sin(F1 - f) * cos(f + pi / 2)
                    space_objects[i].vy = ((v1 * cos(F1 - f) * (m1 - m2) + 2 * m2 * v2 * cos(F2 - f)) * sin(f)) \
                        / (m1 + m2) + v1 * sin(F1 - f) * sin(f + pi / 2)

                    space_objects[j].vx = ((v2 * cos(F2 - f) * (m2 - m1) + 2 * m1 * v1 * cos(F1 - f)) * cos(f)) \
                        / (m1 + m2) + v2 * sin(F2 - f) * cos(f + pi / 2)
                    space_objects[j].vy = ((v2 * cos(F2 - f) * (m2 - m1) + 2 * m1 * v1 * cos(F1 - f)) * sin(f)) \
                        / (m1 + m2) + v2 * sin(F2 - f) * sin(f + pi / 2)
                    space_objects[i].switch = 0
                    break
        else:
            space_objects[i].switch = 1
    for i in range(len(space_objects)):
        space_objects[i].x += space_objects[i].vx * dt
        space_objects[i].y += space_objects[i].vy * dt


if __name__ == '__main__':
    pygame.draw.rect(user.screen, '#005ffe', pygame.Rect(480, 490, 960 * 0.25, 50))
    pygame.display.update()

    zoom = 1
    moving_right, moving_left, moving_up, moving_down = False, False, False, False
    movement_speed = 4
    movement = [0, 0]

    pygame.display.set_caption('Space_physics')
    clock = pygame.time.Clock()
    display = pygame.Surface((user.size[0], user.size[1]))
    G = 1000
    speed = 1
    dt = (1 / user.fps) * speed # шаг времени для объектов
    pygame.draw.rect(user.screen, '#005ffe', pygame.Rect(480, 490, 960 * 0.5, 50))
    pygame.display.update()

    star_img = pygame.image.load('data/star.png')
    planet_img = pygame.image.load('data/plan.png')
    hole_img = pygame.image.load('data/sun.png')
    space_objects = []
    pygame.draw.rect(user.screen, '#005ffe', pygame.Rect(480, 490, 960 * 0.75, 50))
    pygame.display.update()

    simulation_name = '2mov_1stay'
    simulation(space_objects, simulation_name)
    
    waiting = True
    koef = 1
    switch = 1
    while waiting: # ожидание ответа пользователя
        pygame.draw.rect(user.screen, '#005ffe', pygame.Rect(480, 490, 960, 50))
        user.screen.blit(dwnld_text1, (user.size[0] // 2 - dwnld_text1.get_rect().width // 2, 550))
        user.screen.blit(dwnld_text2, (user.size[0] // 2 - dwnld_text2.get_rect().width // 2, 580))
        dwnld_text3 = font.render("Нажмите любую клавишу", True, (180 * koef, 180 * koef, 180 * koef))
        user.screen.blit(dwnld_text3, (user.size[0] // 2 - dwnld_text3.get_rect().width // 2, 610))
        pygame.display.update()
        user.screen.fill((0, 0, 0))
        if switch and koef > 0.6:
            koef -= 0.1
        else:
            switch = 0
        if not(switch) and koef < 1:
            koef += 0.1
        else:
            switch = 1
        for event in pygame.event.get():
            if event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
                waiting = False
                break
        sleep(0.1)
    del(koef)
    del(waiting)
    del(switch)

    running = True
    pause = True
    mode = False
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
                if event.key == K_e:
                    if not(mode): mode = True
                    else: mode = False
                if event.key == K_0:
                    space_objects = []
                    simulation(space_objects, simulation_name)
                if event.key == K_p:
                    while pause:
                        for event in pygame.event.get():
                            if event.type == KEYDOWN:
                                if event.key == K_p:
                                    pause = False
                                    break
                                if event.key == K_ESCAPE:
                                    running = False
                                    pause = False
                                    break
                        sleep(0.1)
                    pause = True
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4: # вперед
                    zoom += 0.1
                    if zoom > 4:
                        zoom += 0.1
                    zoom = round(zoom, 1)
                elif event.button == 5: # назад
                    if zoom > 0.1:
                        zoom -= 0.1
                        zoom = round(zoom, 1)
                elif event.button == 1: # ЛКМ
                    aStar = obj(int(event.pos[0] / zoom - movement[0]), int(event.pos[1] / zoom - movement[1]), star_img, 16.0, 1.0)
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
            movement[1] += movement_speed / zoom
        if moving_down:
            movement[1] -= movement_speed / zoom
        if moving_left:
            movement[0] += movement_speed / zoom
        if moving_right:
            movement[0] -= movement_speed / zoom
        display.fill((0, 0, 0))
        step()
        for i in range(len(space_objects)): # отрисовка объектов
            space_objects[i].draw(zoom, mode)

        user.screen.blit(display, (0, 0))
        fps_val()
        pygame.display.update()
        clock.tick(user.fps)

    pygame.quit()
    exit('Exit')