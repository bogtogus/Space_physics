import pygame
from pygame.locals import *
from time import time, sleep, strftime, strptime, ctime
from math import cos, sin, asin, pi, sqrt, degrees, atan2, radians, floor
import os, traceback, sqlite3


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
update_rect = pygame.Rect(user.size[0] // 4, user.size[1] // 2 - 50, user.size[0] // 2, user.size[1] // 4)
coefficient = floor(user.size[0] / 1920)
deafult_font = pygame.font.Font('data/Anonymous Pro B.ttf', 24 * coefficient)
obj_info_font = pygame.font.Font('data/Anonymous Pro B.ttf', 16 * coefficient)
sim_info_font = pygame.font.Font('data/Anonymous Pro B.ttf', 24)
#dwnld_text1 = font.render("'W', 'A', 'S', 'D' - движение | Колёсико мыши - масштаб | P - пауза", True, '#c8c8c8')
#dwnld_text2 = font.render("E - расширенный режим | 0 - сброс", True, '#c8c8c8')


class obj:
    def __init__(self, x, y, img, r, m, vx = 0, vy = 0):
        self.x = x
        self.y = y
        self.r = r
        self.m = m
        self.img = img
        self.vx = 0
        self.vy = 0
        self.coll = 0 # collision state (0 if collision happened)
    def draw(self, zoom, movement: list, mode: bool):
        if (self.vy != 0 or self.vx != 0) and mode:
            sin_ = self.vy / ((self.vy * self.vy + self.vx * self.vx) ** 0.5)
            cos_ = self.vx / ((self.vy * self.vy + self.vx * self.vx) ** 0.5)
            x_coord = (self.x + movement[0] + 10 + self.r) * zoom
            y_coord = (self.y + movement[1] - self.r) * zoom
            start = [(self.x + movement[0]) * zoom, (self.y + movement[1]) * zoom]
            end = [(self.x + movement[0] + 100 * cos_) * zoom, (self.y + movement[1] + 100 * sin_) * zoom]
            pygame.draw.line(display, '#c80000', start, end, 2) # direction line
            rotation = degrees(atan2(start[1] - end[1], end[0] - start[0])) + 90
            pygame.draw.polygon(display, '#c80000', ((end[0] + (10 * sin(radians(rotation))) * zoom, end[1] + (10 * cos(radians(rotation))) * zoom), (end[0] + (5 * sin(radians(rotation - 120))) * zoom, end[1] + (5 * cos(radians(rotation - 120))) * zoom), (end[0] + (5 * sin(radians(rotation + 120))) * zoom, end[1] + (5 * cos(radians(rotation + 120))) * zoom)))
            display.blit(obj_info_font.render("vx, vy: {}, {}".format(round(self.vx, 3), round(self.vy, 3)), True, '#c8c8c8'), (x_coord, y_coord - 26))
            display.blit(obj_info_font.render("m: " + str(self.m), True, '#c8c8c8'), (x_coord, y_coord - 10))
            display.blit(obj_info_font.render("coll: " + str(self.coll), True, '#c8c8c8'), (x_coord, y_coord + 6))
        display.blit(pygame.transform.scale(self.img, (int(self.img.get_width() * zoom), \
            int(self.img.get_height() * zoom))), \
            # x:
            (int((self.x + movement[0] - self.r) * zoom), \
            # y:
            int((self.y + movement[1] - self.r) * zoom)))


class button():
    def __init__(self, place=(0, 0), size=(0, 0), color='#c8c8c8', button_text='', font_size=16, font_color='#000000', path='data/Anonymous Pro B.ttf'):
        self.font = pygame.font.Font(path, font_size)
        self.font_color = font_color
        self.color = color
        self.select = False
        self.select_color = '#005ffe'
        self.text = button_text
        self.print_text = self.font.render(self.text, True, self.font_color)
        self.place = list(place)
        self.size = size
        text_x = self.place[0] + self.size[0] // 2 - self.print_text.get_width() // 2
        text_y = self.place[1] + self.size[1] // 2 - self.print_text.get_height() // 2
        self.text_pos = [text_x, text_y]
        self.body = pygame.Rect(self.place[0], self.place[1], self.size[0], self.size[1])
    def update(self):
        self.print_text = self.font.render(self.text, True, self.font_color)
        self.place = self.place
        self.body = pygame.Rect(self.place[0], self.place[1], self.size[0], self.size[1])
        text_x = self.place[0] + self.size[0] // 2 - self.print_text.get_width() // 2
        text_y = self.place[1] + self.size[1] // 2 - self.print_text.get_height() // 2
        self.text_pos = [text_x, text_y]
    def draw(self):
        if not(self.select):
            pygame.draw.rect(user.screen, self.color, self.body)
        else:
            pygame.draw.rect(user.screen, self.select_color, self.body)
            pygame.draw.rect(user.screen, '#c8c8c8', self.body, 1)
        user.screen.blit(self.print_text, self.text_pos)

""" ========= Technical functions ========= """

def simulation(mass: list, name: str): # creating a list of sim. objects 
        try:
            with open('simulations/' + name + '/sim.data', 'r') as doc:
                sim = doc.readlines()
                sim = list(map(lambda x: x.split(), sim))
            mass = []
            for i in range(len(sim)):
                if len(sim[i]) != 5 and len(sim[i]) != 7:
                    continue
                aStar = obj(float(sim[i][0]), float(sim[i][1]), globals()[sim[i][2]], float(sim[i][3]), float(sim[i][4]))
                if len(sim[i]) > 5: #vx, vy
                    aStar.vx = float(sim[i][5])
                    aStar.vy = float(sim[i][6])
                mass.append(aStar)
            if len(mass) == 0:
                mass = ['error', 'List is empty.']
        except Exception:
            with open('log.txt', 'a') as log:
                log.write('\n{} [{}]\n'.format(traceback.format_exc(), strftime('%x %X', strptime(ctime()))))
            mass = ['error', 'An error has occurred. Check log.txt.']
        return mass


def init_content(): # creating all main dicts, lists and getting current language
    simulations = []
    languages = []
    bkgr = [] # background
    sim_images = {}
    sim_info = {}
    menu_buttons = {}
    db = sqlite3.connect('C:/Users/BOGDAN/Documents/GitHub/Space_physics/database.db')
    sql = db.cursor()
    for i in sql.execute("SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%'"): # languages
        if i[0] != 'settings' and len(i[0]) == 2:
            languages.append(i[0])
    curr_lang = sql.execute("SELECT language FROM settings WHERE user ='user01'").fetchone()[0]
    for i in sql.execute("SELECT class, name, text, color, font_color FROM {}".format(curr_lang)): # buttons
        if i[0] == 'button':
            init_button = button(place=(0, 0), size=(400, 70), color=i[3], button_text=i[2], font_size=30, font_color=i[4])
            menu_buttons.update({i[1]: init_button})
    menu_buttons['choose_button'].place = [user.size[0] // 2 - 200, user.size[1] // 2]
    menu_buttons['settings_button'].place = [user.size[0] // 2 - 200, user.size[1] // 2 + 105]
    menu_buttons['exit_button'].place = [user.size[0] // 2 - 200, user.size[1] // 2 + 210]
    menu_buttons['lang_button'].place = [user.size[0] // 2 - 100, user.size[1] // 2]
    menu_buttons['lang_table'].place = [user.size[0] // 2 - 350, user.size[1] // 2]
    menu_buttons['lang_button'].size = (200, 70)
    menu_buttons['lang_table'].size = (200, 70)
    for b in menu_buttons.keys():
        menu_buttons[b].update()
    
    for item in os.listdir('simulations/'): # simulations, images and info
        if not(item.startswith('.')) and not(os.path.isfile(os.path.join('simulations/', item))):
            simulations.append(item)
            try:
                image = pygame.image.load('simulations/' + item + '/preview.png').convert()
                sim_images.update({item: image})
            except Exception:
                image = pygame.image.load('simulations/noimage.png').convert()
                sim_images.update({item: image})
            try:
                text = sql.execute("SELECT class, name, text FROM '{}' WHERE class = 'info' and name = '{}'".format(curr_lang, item)).fetchone()[2]
                text = text.replace('\n', ' ')
            except Exception:
                text = "Text doesn't exist."
            text = split_by_spaces(text, 43)
            text = list(text)
            sim_info.update({item: text})
    sim_images.update({'noimage': pygame.image.load('simulations/noimage.png').convert()})
    for i in range(1, 16):
        bkgr.append(pygame.image.load('data/backgr/backgr2_' + str(i) + '.png'))
    db.close()
    return simulations, sim_images, sim_info, menu_buttons, bkgr, languages, curr_lang


def split_by_spaces(string, length):
    upper_border = 0
    output = []
    try:
        while len(string) > 0:
            if len(string) <= length:
                output.append(string.strip())
                break
            upper_border = string.rindex(' ', 0, length + 1)
            output.append(string[:upper_border].strip())
            string = string[upper_border + 1:len(string)]
    except ValueError:
        with open('log.txt', 'a') as log:
            log.write('ValueError [' + strftime('%x %X', strptime(ctime())) + ']\n')
        string = 'An error has occurred.'
    return output


def draw_text(text='empty', path='data/Anonymous Pro B.ttf', size=16, color='#c8c8c8', place=(0, 0)): # this function is slow
    place = list(place)
    font = pygame.font.Font(path, size)
    print_text = font.render(text, True, color)
    if type(place[0]) == type(True):
        place[0] = user.size[0] // 2 - print_text.get_width() // 2
    if type(place[1]) == type(True):
        place[1] = user.size[1] // 2 - print_text.get_height() // 2
    user.screen.blit(print_text, place)


cur_time = int(round(time() * 1000))
cadrs = 0
fps = 0
def fps_val(game=True, zoom_=1, movement=[0, 0]): # value of fraps per second
    global cur_time, cadrs, fps
    if int(round(time() * 1000)) - cur_time > 1000:
        fps = cadrs
        cadrs = 0
        cur_time = int(round(time() * 1000))
    if game:
        data = '{} fps, {} obj, zoom: {}, [end]: {}, Real: {}'.format(fps, len(space_objects), zoom_,
            (int((space_objects[-1].x + movement[0]) * zoom_), int((space_objects[-1].y + movement[1]) * zoom_)),
            (int(space_objects[-1].x), int(space_objects[-1].y)))
    else:
        data = str(fps) + ' fps'
    user.screen.blit(deafult_font.render(data, True, '#c8c8c8'), (0, 0))
    cadrs += 1


def step():
    for i in range(len(space_objects)): # current
        i_obj = space_objects[i]
        for j in range(len(space_objects)): # another
            if i == j: continue
            j_obj = space_objects[j]
            if i_obj.coll or space_objects[j].coll: continue
            dx = j_obj.x - i_obj.x
            dy = j_obj.y - i_obj.y
            r = dx * dx + dy * dy # R^2
            if r > (j_obj.r + i_obj.r) * (j_obj.r + i_obj.r):
                a = G * j_obj.m / r
                r = sqrt(r) # R
                if r < 0.1: r = 0.1
                ax = a * dx / r # a * cos
                ay = a * dy / r # a * sin
                space_objects[i].vx += ax * dt
                space_objects[i].vy += ay * dt
            else:
                r = sqrt(r)
                if r < 0.01: r = 0.01
                v_x1 = i_obj.vx
                v_y1 = i_obj.vy
                v1 = sqrt(v_x1 * v_x1 + v_y1 * v_y1)
                m1 = i_obj.m
            
                v_x2 = j_obj.vx
                v_y2 = j_obj.vy
                v2 = sqrt(v_x2 * v_x2 + v_y2 * v_y2)
                m2 = j_obj.m
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
                space_objects[i].coll = 1
                break
        else:
            space_objects[i].coll = 0
    for i in range(len(space_objects)):
        space_objects[i].x += space_objects[i].vx * dt
        space_objects[i].y += space_objects[i].vy * dt

""" ========= GUI functions ========= """

def settings_window(langs, curr_lang, buttons, sim_i):
    user.screen.fill('#000000')
    settings_cycle = True
    click = False
    k = 0 # counter for background
    while settings_cycle:
        backgrrect = (0, 0)
        user.screen.blit(pygame.transform.scale(bkgr[k//5], (user.size[0], user.size[1])), backgrrect)
        k += 1
        if k == 50:
            k = 0
        buttons['lang_button'].draw()
        buttons['lang_table'].draw()
        mx, my = pygame.mouse.get_pos()
        if buttons['lang_button'].body.collidepoint((mx, my)) and click: # switch language
            db = sqlite3.connect('C:/Users/BOGDAN/Documents/GitHub/Space_physics/database.db')
            sql = db.cursor()
            for i in range(len(langs)):
                if langs[i] == curr_lang:
                    if i == len(langs) - 1: 
                        curr_lang = langs[0]
                    else:
                        curr_lang = langs[i + 1]
                    break
            for i in sql.execute("SELECT class, name, text FROM {}".format(curr_lang)): # buttons
                if i[0] == 'button':
                    buttons[i[1]].text = i[2]
                    buttons[i[1]].update()
                elif i[0] == 'info':
                    text = split_by_spaces(i[2], 43)
                    text = list(text)
                    sim_i[i[1]] = text
            db.close()
        click = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # LB
                    click = True
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    settings_cycle = False
                    break
            if event.type == pygame.QUIT:
                settings_cycle = False
                break
        fps_val(False)
        pygame.display.update()
        clock.tick(user.fps)
    return curr_lang, buttons, sim_i


def choosing(s_button=None, sim_info=None):
    user.screen.fill('#000000')
    sim_buttons = []
    for i in range(len(simulations)):
        sim_buttons.append(button(place=(user.size[0] // 2 - 200, 35 + 105 * i), size=(400, 70), color='#545454', button_text=simulations[i], font_size=30, font_color='#dddddd'))
        sim_buttons[i].draw()
    start_button = s_button
    start_button.size = (560, 70)
    start_button.place = [user.size[0] // 2 + sim_buttons[0].size[0]//2 + 35, 980]
    start_button.update()
    choose_cycle = True
    click = img = pre_selected = False
    k = 0 # counter for background
    last_pre_selected = ''
    pre_selected = ''
    i_pre_selected = 0
    text = None
    text_backgr = pygame.Rect(user.size[0] // 2 + sim_buttons[0].size[0]//2 + 35, 540 + 70, 560, 370)
    st = 0 # starting point of text generation 
    en = 11 # ending point of text generation 
    while choose_cycle:
        mx, my = pygame.mouse.get_pos()
        for i in range(len(sim_buttons)): # if user clicked on simulation
            if sim_buttons[i].body.collidepoint((mx, my)) and click:
                sim_buttons[i_pre_selected].select = False
                pre_selected = sim_buttons[i].text
                i_pre_selected = i
                sim_buttons[i].select = True
                st = 0
                break
        if start_button.body.collidepoint((mx, my)) and click and pre_selected: # if user clicked on start
            choose_cycle = False
            selected_sim = pre_selected
            user.screen.fill('#000000')
            return choose_cycle, selected_sim
        click = False
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1: # LB
                    click = True
                    break
                elif event.button == 4: # mouse wheel forward
                    if - sim_buttons[0].size[0] // 2 < mx - user.size[0] // 2 < sim_buttons[0].size[0] // 2: # cursor in buttons' width area 
                        if sim_buttons[0].place[1] < 35: # buttons' top limit
                            for i in range(len(sim_buttons)):
                                sim_buttons[i].place[1] += 35
                                sim_buttons[i].update()
                    elif text_backgr.collidepoint((mx, my)) and text and len(text) > 12 and st > 0: # scrolling the text up
                        st -= 1
                        en -= 1
                elif event.button == 5: # backward
                    if - sim_buttons[0].size[0] // 2 < mx - user.size[0] // 2 < sim_buttons[0].size[0] // 2:
                        if sim_buttons[-1].place[1] >= user.size[1] - sim_buttons[-1].size[1] // 2 - 35: # buttons' bottom limit
                            for i in range(len(sim_buttons)):
                                sim_buttons[i].place[1] -= 35
                                sim_buttons[i].update()
                    elif text_backgr.collidepoint((mx, my)) and text and len(text) > 12 and en < len(text): # scrolling the text down
                        st += 1
                        en += 1
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    choose_cycle = False
                    break
            if event.type == pygame.QUIT:
                print('Abrupt exit')
                raise SystemExit(1)
        pygame.draw.rect(user.screen, '#c8c8c8', text_backgr, 1)
        user.screen.blit(pygame.transform.scale(bkgr[k//5], (user.size[0], user.size[1])), (0, 0))
        k += 1
        if k == 75: k = 0 # if k out of limit
        for i in range(len(sim_buttons)):
            sim_buttons[i].draw()
        if pre_selected:
            if pre_selected != last_pre_selected: # avoidance of repeating
                img = sim_images[pre_selected]
                imgrect = img.get_rect(topleft=(user.size[0]//2 + 45 + sim_buttons[0].size[0]//2, 45))
                img_backg = pygame.Rect(imgrect[0] - 10, imgrect[1] - 10, img.get_width() + 20, img.get_height() + 20)
                text = sim_info[pre_selected]
                if len(text) > 12:
                    en = 12
                else:
                    en = len(text)
                last_pre_selected = pre_selected
            pygame.draw.rect(user.screen, '#c8c8c8', img_backg)
            user.screen.blit(img, imgrect)
            o = 0 # text wrapping
            for i in range(st, en):
                if o < 360:
                    print_text = sim_info_font.render(text[i], True, '#c8c8c8')
                    user.screen.blit(print_text, (user.size[0] // 2 + sim_buttons[0].size[0]//2 + 35, 540 + 70 + o))
                    o += 30
            start_button.draw()
        fps_val(False)
        pygame.display.update()
        clock.tick(user.fps)
    return True, None


def main_menu(error=None, langs=None, lang=None, buttons=None, sim_i=None):
    user.screen.fill('#000000')
    menu_cycle = True
    click = False
    k = 0 # counter for background
    if error:
        error_text = deafult_font.render(error, True, '#ee1111')
        error_window = button(place=(35, user.size[1] - 75), size=(error_text.get_width() + 70, 50), color='#990000', button_text=error, font_size=24, font_color='#dddddd')
        error_window_time = int(round(time() * 1000))
    while menu_cycle:
        backgrrect = (0, 0)
        user.screen.blit(pygame.transform.scale(bkgr[k//5], (user.size[0], user.size[1])), backgrrect)
        k += 1
        if k == 50:
            k = 0
        buttons['choose_button'].draw()
        buttons['settings_button'].draw()
        buttons['exit_button'].draw()
        mx, my = pygame.mouse.get_pos()
        if buttons['choose_button'].body.collidepoint((mx, my)) and click:
            menu_cycle, selected_sim = choosing(menu_buttons['start_button'], sim_i)
            if menu_cycle:
                user.screen.blit(pygame.transform.scale(bkgr[k//5], (user.size[0], user.size[1])), backgrrect)
                buttons['choose_button'].draw()
                buttons['settings_button'].draw()
                buttons['exit_button'].draw()
        elif buttons['settings_button'].body.collidepoint((mx, my)) and click:
            lang, buttons, sim_i = settings_window(langs, lang, buttons, sim_i)
        elif buttons['exit_button'].body.collidepoint((mx, my)) and click: # exit button
            return None, lang, False
        click = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # LB
                    click = True
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    return None, lang, False
            if event.type == pygame.QUIT:
                return None, lang, False
        fps_val(False)
        if error and int(round(time() * 1000)) - error_window_time < 5000:
            error_window.draw()
        pygame.display.update()
        clock.tick(user.fps)
    user.screen.fill('#000000')
    return selected_sim, lang, True


def simulation_loop(space_objects, simulation_name):
    zoom = 1.0
    movement_speed, movement = 4, [0, 0]
    moving_right = moving_left = moving_up = moving_down = False
    sim_cycle = True
    pause = mode = False
    while sim_cycle:
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
                    sim_cycle = False
                    break
                if event.key == K_e:
                    if not(mode): mode = True
                    else: mode = False
                if event.key == K_0:
                    space_objects = []
                    space_objects = simulation(space_objects, simulation_name)
                if event.key == K_p:
                    pause = True
                    while pause:
                        for event in pygame.event.get():
                            if event.type == KEYDOWN:
                                if event.key == K_p:
                                    pause = False
                                    break
                                if event.key == K_ESCAPE:
                                    sim_cycle = pause = False
                                    break
                            if event.type == pygame.QUIT:
                                sim_cycle = pause = False
                                break
                        sleep(0.1)
            
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4: # mouse wheel forward
                    zoom += 0.1
                    if zoom > 4:
                        zoom += 0.1
                    zoom = round(zoom, 1)
                elif event.button == 5: # backward
                    if zoom > 0.1:
                        zoom -= 0.1
                        zoom = round(zoom, 1)
                elif event.button == 1: # LBM
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
            
            if event.type == pygame.QUIT:
                sim_cycle = False
        if moving_up:
            movement[1] += movement_speed / zoom
        if moving_down:
            movement[1] -= movement_speed / zoom
        if moving_left:
            movement[0] += movement_speed / zoom
        if moving_right:
            movement[0] -= movement_speed / zoom
        display.fill('#000000')
        step()
        for i in range(len(space_objects)): # drawing objects
            space_objects[i].draw(zoom, movement, mode)

        user.screen.blit(display, (0, 0))
        fps_val(zoom_=zoom, movement=movement)
        pygame.display.update()
        clock.tick(user.fps)
    simulation_name = ''
    space_objects = ['', '']


if __name__ == '__main__':
    pygame.display.set_caption('Space_physics')
    clock = pygame.time.Clock()
    display = pygame.Surface((user.size[0], user.size[1]))
    display.set_alpha(None)
    G = 1000.0 # real value = 6.67430e-11. You will need to use decimal or waiting for updates to calculate that
    speed = 1 # simulation speed
    dt = (1 / user.fps) * speed # time step for objects

    star_img = pygame.image.load('data/star.png').convert()
    planet_img = pygame.image.load('data/plan.png')
    hole_img = pygame.image.load('data/sun.png').convert()
    
    simulations, sim_images, sim_info, menu_buttons, bkgr, languages, curr_lang = init_content()

    simulation_name = ''
    space_objects = ['', '']
    main_loop = True
    error = None
    while main_loop:
        simulation_name, curr_lang, main_loop = main_menu(error, languages, curr_lang, menu_buttons, sim_info)
        if simulation_name:
            space_objects = simulation(space_objects, simulation_name)
            if space_objects[0] != 'error':
                simulation_loop(space_objects, simulation_name)
                error = None
            else:
                error = space_objects[1]
    
    db = sqlite3.connect('C:/Users/BOGDAN/Documents/GitHub/Space_physics/database.db')
    sql = db.cursor()
    sql.execute("UPDATE settings SET language = '{}' WHERE user = 'user01'".format(curr_lang))
    db.commit()
    db.close()
    pygame.quit()
    exit('Exit')
