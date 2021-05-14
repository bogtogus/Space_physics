import pygame
from pygame.locals import *
from time import time, sleep, strftime, strptime, ctime
from math import cos, sin, asin, pi, sqrt, degrees, atan2, radians, ceil, hypot, log
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
pygame.display.set_caption('Space_physics')
if user.size[0] / 1920 < user.size[1] / 1080: # transformation ratio of all GUI elements
    COEFFICIENT = user.size[0] / 1920
else:
    COEFFICIENT = user.size[1] / 1080
DIST_COEFF = 1e-6 # distance coefficient transformates meters to megameters
G = 6.67430e-11 # real value = 6.67430e-11. You will need to use decimal or waiting for updates to calculate that
SPEED = 60*60*24 # simulation speed
DT = (1 / user.fps) * SPEED # time step for objects
deafult_font = pygame.font.Font('data/Anonymous Pro B.ttf', round(24 * COEFFICIENT))
obj_info_font = pygame.font.Font('data/Anonymous Pro B.ttf', round(16 * COEFFICIENT))
help_font = pygame.font.Font('data/Anonymous Pro B.ttf', round(30 * COEFFICIENT))
f_s = 1 # font size
sim_info_font = pygame.font.Font('data/Anonymous Pro B.ttf', f_s)
while (560 * COEFFICIENT) / sim_info_font.render("a", True, '#c8c8c8').get_width() >= 43: # calculating necessary font size
    f_s += 1
    sim_info_font = pygame.font.Font('data/Anonymous Pro B.ttf', f_s)
del(f_s)


class obj:
    def __init__(self, x, y, img, r, m, vx = 0.0, vy = 0.0):
        self.x = x # object class stores all physical quantities in the SI system
        self.y = y
        self.r = r
        self.m = m
        self.vx = vx
        self.vy = vy
        self.img = img
        self.transformed_img = img
        self.coll = False # collision state (True if collision happened)
    def update(self, zoom: float):
        if self.img == 'circle': return None
        if self.img.get_width() * zoom > 3 and self.img.get_height() * zoom > 3:
            self.transformed_img = pygame.transform.scale(self.img, (int(self.img.get_width() * zoom), int(self.img.get_height() * zoom)))
        else:
            self.transformed_img = pygame.transform.scale(self.img, (3, 3))
    def draw(self, zoom: float, movement: list, mode: bool, COEFFICIENT: float, DIST_COEFF: float):
        pos_on_display = ((self.x * DIST_COEFF + movement[0]) * zoom, (self.y * DIST_COEFF + movement[1]) * zoom)
        if pos_on_display[0] > user.size[0] or pos_on_display[0] < 0 or pos_on_display[1] > user.size[1] or pos_on_display[1] < 0: return None
        if self.img == 'circle':
            if self.r * DIST_COEFF * zoom > 2:
                pygame.draw.circle(display_surf, '#777777', (int((self.x * DIST_COEFF + movement[0]) * zoom),
                    int((self.y * DIST_COEFF + movement[1]) * zoom)), self.r * DIST_COEFF * zoom)
            else:
                pygame.draw.circle(display_surf, '#777777', (int((self.x * DIST_COEFF + movement[0]) * zoom),
                    int((self.y * DIST_COEFF + movement[1]) * zoom)), 2)
        else:
            display_surf.blit(self.transformed_img, (int((self.x * DIST_COEFF + movement[0]) * zoom - self.transformed_img.get_width() // 2),
                int((self.y * DIST_COEFF + movement[1]) * zoom - self.transformed_img.get_height() // 2)))
        if mode:
            if self.img == 'circle':
                x_coord = (self.x * DIST_COEFF + movement[0]) * zoom + self.r * DIST_COEFF * zoom # coordinates of the text 
                y_coord = (self.y * DIST_COEFF + movement[1]) * zoom - self.r * DIST_COEFF * zoom
            else:
                x_coord = (self.x * DIST_COEFF + movement[0]) * zoom + self.transformed_img.get_width() // 2
                y_coord = (self.y * DIST_COEFF + movement[1]) * zoom - self.transformed_img.get_height() // 2
            if (self.vy != 0 or self.vx != 0):
                sin_ = self.vy / (hypot(self.vy, self.vx))
                cos_ = self.vx / (hypot(self.vy, self.vx))
                start = [(self.x * DIST_COEFF + movement[0]) * zoom, (self.y * DIST_COEFF + movement[1]) * zoom] # start point of line
                end = [(self.x * DIST_COEFF + movement[0] + 100 * cos_) * zoom, (self.y * DIST_COEFF + movement[1] + 100 * sin_) * zoom] # end point of line
                pygame.draw.line(display_surf, '#c80000', start, end, 2) # direction line
                rotation = degrees(atan2(start[1] - end[1], end[0] - start[0])) + 90
                pygame.draw.polygon(display_surf, '#c80000', ((end[0] + (10 * sin(radians(rotation))) * zoom, end[1] + (10 * cos(radians(rotation))) * zoom), (end[0] + (5 * sin(radians(rotation - 120))) * zoom, end[1] + (5 * cos(radians(rotation - 120))) * zoom), (end[0] + (5 * sin(radians(rotation + 120))) * zoom, end[1] + (5 * cos(radians(rotation + 120))) * zoom))) # arrowhead
            display_surf.blit(obj_info_font.render("vx, vy: {}, {} km/s".format(round(self.vx / 1000, 3), round(self.vy / 1000, 3)), True, '#c8c8c8'), (x_coord, y_coord - 26 * COEFFICIENT))
            display_surf.blit(obj_info_font.render("m: " + str(self.m) + ' kg', True, '#c8c8c8'), (x_coord, y_coord - 10 * COEFFICIENT))
            display_surf.blit(obj_info_font.render("coll: " + str(self.coll), True, '#c8c8c8'), (x_coord, y_coord + 6 * COEFFICIENT))
            display_surf.blit(obj_info_font.render("vx, vy: {}, {} km/s".format(round(self.vx / 1000, 3), round(self.vy / 1000, 3)), True, '#c8c8c8'), (x_coord, y_coord - 26 * COEFFICIENT))
    def __str__(self):
        return "Coordinates: ({}, {}), velocity: ({}, {}), radius: {}, mass: {}".format(self.x, self.y, self.vx. self.vy, self.r, self.m)

class button():
    def __init__(self, place=[0, 0], size=(0, 0), color='#c8c8c8', button_text='', font_size=16, font_color='#000000', path='data/Anonymous Pro B.ttf'):
        self.place = place
        self.size = size
        self.body = pygame.Rect(self.place[0], self.place[1], self.size[0], self.size[1])
        self.color = color
        self.select = False
        self.select_color = '#005ffe'
        self.text = button_text
        self.font = pygame.font.Font(path, font_size)
        self.font_color = font_color
        self.print_text = self.font.render(self.text, True, self.font_color)
        text_x = self.place[0] + self.size[0] // 2 - self.print_text.get_width() // 2
        text_y = self.place[1] + self.size[1] // 2 - self.print_text.get_height() // 2
        self.text_pos = [text_x, text_y]
    def update(self):
        self.print_text = self.font.render(self.text, True, self.font_color)
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

def init_simulation(obj_list: list, name: str, images: dict, COEFFICIENT=1): 
    """Creates a list of simulanion's objects."""
    try:
        with open('simulations/' + name + '/sim.data', 'r') as doc:
            sim = doc.readlines()
            sim = list(map(lambda x: x.split(), sim))
        if len(sim) > 1000:
            load = 0
            load_rect = pygame.Rect(user.size[0] // 2 - 500 * COEFFICIENT, user.size[1] // 2 - user.size[1] / 31, load * 10 * COEFFICIENT, user.size[1] / 31)
            pygame.draw.rect(user.screen, '#666666', (user.size[0] // 2 - 500 * COEFFICIENT, user.size[1] // 2 - user.size[1] / 31, 1000 * COEFFICIENT, user.size[1] / 31))
        obj_list = []
        for i in range(len(sim)):
            if len(sim[i]) != 5 and len(sim[i]) != 7: continue
            try: img = images[sim[i][2]]
            except: img = 'circle'
            aStar = obj(float(sim[i][0]), float(sim[i][1]), img, float(sim[i][3]), float(sim[i][4]))
            if len(sim[i]) > 5: #vx, vy
                aStar.vx = float(sim[i][5])
                aStar.vy = float(sim[i][6])
            obj_list.append(aStar)
            if len(sim) > 1000 and i / len(sim) * 100 >= load:
                load += 10
                load_rect.width = load * 10 * COEFFICIENT
                pygame.draw.rect(user.screen, '#ffffff', load_rect)
                pygame.display.update()
        if len(obj_list) == 0:
            obj_list = ['error', 'List is empty.']
    except Exception:
        with open('log.txt', 'a') as log:
            log.write('\n{} [{}]\n'.format(traceback.format_exc(), strftime('%x %X', strptime(ctime()))))
        obj_list = ['error', 'An error has occurred. Check log.txt.']
    return obj_list


def init_content(COEFFICIENT=1): 
    """Creates all main dicts, lists and getting current language."""
    simulations_content = {}
    languages = {"languages": [], "curr_lang": None}
    menu_buttons = {}
    text_dict = {}
    images = {"objects": {}, "background": [], "logo": None}

    height = 2 * user.size[1] / 31
    db = sqlite3.connect('database.db')
    sql = db.cursor()
    for i in sql.execute("SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%'"): # languages
        if i[0] != 'settings' and len(i[0]) == 2:
            languages["languages"].append(i[0])
    languages["curr_lang"] = sql.execute("SELECT language FROM settings WHERE user ='user01'").fetchone()[0]
    for i in sql.execute("SELECT class, name, text, color, font_color FROM {}".format(languages['curr_lang'])): # buttons
        if i[0] == 'button':
            init_button = button(place=[0, 0], size=(round(400 * COEFFICIENT), height), color=i[3], button_text=i[2], font_size=round(30 * COEFFICIENT), font_color=i[4])
            menu_buttons.update({i[1]: init_button})
    menu_buttons['continue_button'].place = [user.size[0] // 2 - menu_buttons['choose_button'].size[0] // 2, user.size[1] // 2]
    menu_buttons['save_button'].place = [user.size[0] // 2 - menu_buttons['settings_button'].size[0] // 2, user.size[1] // 2 + menu_buttons['settings_button'].size[1] * 1.5]
    menu_buttons['choose_button'].place = [user.size[0] // 2 - menu_buttons['choose_button'].size[0] // 2, user.size[1] // 2]
    menu_buttons['settings_button'].place = [user.size[0] // 2 - menu_buttons['settings_button'].size[0] // 2, user.size[1] // 2 + menu_buttons['settings_button'].size[1] * 1.5]
    menu_buttons['help_button'].place = [user.size[0] // 2 - menu_buttons['help_button'].size[0] // 2, user.size[1] // 2 + menu_buttons['help_button'].size[1] * 3]
    menu_buttons['exit_button'].place = [user.size[0] // 2 - menu_buttons['exit_button'].size[0] // 2, user.size[1] // 2 + menu_buttons['exit_button'].size[1] * 4.5]
    menu_buttons['lang_button'].size = (round(200 * COEFFICIENT), height)
    menu_buttons['lang_table'].size = (round(200 * COEFFICIENT), height)
    menu_buttons['lang_button'].place = [user.size[0] // 2 - menu_buttons['lang_button'].size[0] // 2, user.size[1] // 2]
    menu_buttons['lang_table'].place = [user.size[0] // 2 - 3.25 * menu_buttons['lang_button'].size[0] // 2, user.size[1] // 2]
    for b in menu_buttons.keys():
        menu_buttons[b].update()
    i = 0
    for item in os.listdir('simulations/'): # simulations's content
        if not(item.startswith('.')) and not(os.path.isfile(os.path.join('simulations/', item))):
            try:
                image = pygame.transform.scale(pygame.image.load('simulations/' + item + '/preview.png').convert(), (round(540 * COEFFICIENT), round(540 * COEFFICIENT)))
            except Exception:
                image = pygame.transform.scale(pygame.image.load('simulations/noimage.png').convert(), (round(540 * COEFFICIENT), round(540 * COEFFICIENT)))
            try:
                text = sql.execute("SELECT text FROM '{}' WHERE class = 'info' and name = '{}'".format(languages['curr_lang'], item)).fetchone()[0]
                text = text.replace('\n', ' ')
            except Exception:
                text = "Text doesn't exist."
            text = split_by_separator(text, 43)
            text = list(text)
            sim_button = button(place=[0, 0], size=(round(400 * COEFFICIENT), height), color='#545454', button_text=item, font_size=round(30 * COEFFICIENT), font_color='#dddddd')
            sim_button.place = [user.size[0] // 2 - sim_button.size[0] // 2, sim_button.size[1] / 2 + sim_button.size[1] * 1.5 * i]
            sim_button.update()
            simulations_content.update({item: [item, sim_button, image, text]})
            i += 1
    menu_buttons['start_button'].size = (round(560 * COEFFICIENT), height)
    menu_buttons['start_button'].place = [user.size[0] // 2 + sim_button.size[0] // 2 + sim_button.size[1] // 2, user.size[1] - sim_button.size[1] * 1.5]
    menu_buttons['start_button'].update()
    help_text = sql.execute("SELECT text FROM '{}' WHERE class = 'text'".format(languages['curr_lang'])).fetchone()[0]
    help_text = split_by_separator(help_text, 43, '|')
    help_text = list(help_text)
    text_dict.update({'help_text': help_text})
    for i in range(1, 16): # animated background
        images['background'].append(pygame.transform.scale(pygame.image.load('data/backgr/backgr2_' + str(i) + '.png'), (user.size[0], user.size[1])))
    for item in os.listdir('data'): # logotype and objects' images
        if item == 'logo.png':
            logo = pygame.image.load('data/logo.png')
            logo = pygame.transform.scale(logo, (int(logo.get_width() * COEFFICIENT), int(logo.get_height() * COEFFICIENT)))
            images['logo'] = logo
        elif len(item.split('.')) == 2 and item.split('.')[1] in ('png', 'jpg'):
            images['objects'].update({str(item.split('.')[0] + '_img'): pygame.image.load('data/' + item).convert_alpha()})
    db.close()
    return simulations_content, menu_buttons, images, languages, text_dict


def split_by_separator(string, length, separator=' '):
    """This function splits received text by a given string length and a separator."""
    upper_border = 0
    output = []
    try:
        while len(string) > 0:
            if len(string) <= length:
                output.append(string.strip())
                break
            upper_border = string.rindex(separator, 0, length + 1)
            output.append(string[:upper_border].strip())
            string = string[upper_border + 1:len(string)]
    except ValueError:
        if separator == ' ':
            with open('log.txt', 'a') as log:
                log.write('ValueError [' + strftime('%x %X', strptime(ctime())) + ']\n')
            string = 'An error has occurred.'
        else:
            upper_border = string.rindex(separator, 0, len(string))
            output.append(string[:upper_border].strip())
            string = string[upper_border + 1:len(string)]
            output.append(string.strip())
    return output


def draw_text(text='empty', path='data/Anonymous Pro B.ttf', size=16, color='#c8c8c8', place=[0, 0], alignment=None): 
    """This function draws text on the screen. Works slowly with multiple calls."""
    font = pygame.font.Font(path, size)
    print_text = font.render(text, True, color)
    if alignment == 'center':
        place[0] = place[0] - print_text.get_width() // 2
        place[1] = place[1] - print_text.get_height() // 2
    user.screen.blit(print_text, place)


cur_time = int(round(time() * 1000))
cadrs = 0
fps = 0
def fps_val(game=True, zoom_=1, movement=[0, 0], space_object=None, obj_amount=0, DT=1, DIST_COEFF=1):
    """Returns value of fraps per second and other stuff."""
    global cur_time, cadrs, fps
    if int(round(time() * 1000)) - cur_time > 1000:
        fps = cadrs
        cadrs = 0
        cur_time = int(round(time() * 1000))
    if game:
        if space_object:
            x, y = (space_object.x, space_object.y)
            data = '{} fps, {} obj, zoom: {}, [last]: {} px, Real: {} m*10^6'.format(fps, obj_amount, zoom_,
            (int((x * DIST_COEFF + movement[0]) * zoom_), int((y * DIST_COEFF + movement[1]) * zoom_)),
            (int(x * DIST_COEFF), int(y * DIST_COEFF)))
        else:
            data = '{} fps, {} obj, zoom: {}'.format(fps, 0, zoom_)
    else:
        data = str(fps) + ' fps'
    user.screen.blit(deafult_font.render(data, True, '#c8c8c8'), (0, 0))
    cadrs += 1


def step(space_objects, pause=False, DT=1.0, G=1.0):
    if pause: return space_objects
    for i in range(len(space_objects)): # current
        i_obj = space_objects[i]
        for j in range(len(space_objects)): # another
            if i == j or i_obj.coll or space_objects[j].coll: continue
            j_obj = space_objects[j]
            dx = j_obj.x - i_obj.x
            dy = j_obj.y - i_obj.y
            r = hypot(dx, dy) # R
            if r > j_obj.r + i_obj.r:
                if r < 0.001: r = 0.001
                a = (G * j_obj.m) / (r * r)
                ax = a * dx / r # a * cos
                ay = a * dy / r # a * sin
                space_objects[i].vx += ax * DT
                space_objects[i].vy += ay * DT
            else:
                if r < 0.001: r = 0.001
                if r < j_obj.r + i_obj.r: # moving an inbound object out of another
                    if i_obj.m <= j_obj.m:
                        space_objects[i].x += (j_obj.vx * DT + (j_obj.r + i_obj.r) - r) * (- dx / r)
                        space_objects[i].y += (j_obj.vy * DT + (j_obj.r + i_obj.r) - r) * (- dy / r)
                    else:
                        break
                    dx = j_obj.x - i_obj.x
                    dy = j_obj.y - i_obj.y
                    r = hypot(dx, dy)
                if r < 0.001: r = 0.001
                v1 = hypot(i_obj.vx, i_obj.vy)
                m1 = i_obj.m
                v2 = hypot(j_obj.vx, j_obj.vy)
                m2 = j_obj.m
                if v1:
                    F1 = asin(i_obj.vy / v1)
                else:
                    F1 = asin(0)
                if v2:
                    F2 = asin(j_obj.vy / v2)
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
                space_objects[i].coll = True
                break
        else:
            space_objects[i].coll = False
    for i in range(len(space_objects) - 1, -1, -1):
        space_objects[i].x += space_objects[i].vx * DT
        space_objects[i].y += space_objects[i].vy * DT
        if abs(space_objects[i].x) > 10 ** 12 or abs(space_objects[i].y) > 10 ** 12: space_objects.pop(i)
    return space_objects

""" ========= GUI functions ========= """

def main_menu(error=None, sim_content=None, langs=None, m_buttons=None, text_dict=None, images=None, COEFFICIENT=1):
    user.screen.fill('#000000')
    bkgr = images['background']
    menu_cycle = True
    click = False
    k = 0 # counter for background
    selected_sim = None
    backgrrect = (0, 0)
    if error:
        error_text = deafult_font.render(error, True, '#ee1111')
        error_window = button(place=[35 * COEFFICIENT, user.size[1] - 75 * COEFFICIENT], size=(error_text.get_width() + 70 * COEFFICIENT, 50 * COEFFICIENT), color='#990000', button_text=error, font_size=round(24 * COEFFICIENT), font_color='#dddddd')
        error_window_time = int(round(time() * 1000))
    while menu_cycle:
        mx, my = pygame.mouse.get_pos()
        if m_buttons['choose_button'].body.collidepoint((mx, my)) and click:
            menu_cycle, selected_sim = choosing_window(m_buttons['start_button'], sim_content, bkgr)
            if selected_sim:
                return True, selected_sim, langs['curr_lang'] # main_loop, simulation_name, curr_lang
            elif not(menu_cycle):
                break
        elif m_buttons['settings_button'].body.collidepoint((mx, my)) and click:
            menu_cycle, langs['curr_lang'], m_buttons, sim_content, text_dict = settings_window(langs, m_buttons, sim_content, text_dict, bkgr)
        elif m_buttons['help_button'].body.collidepoint((mx, my)) and click:
            menu_cycle = help_window(text_dict['help_text'], bkgr)
        elif m_buttons['exit_button'].body.collidepoint((mx, my)) and click: # exit button
            break
        click = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # LB
                    click = True
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    menu_cycle = False
                    break
            if event.type == pygame.QUIT:
                menu_cycle = False
                break
        user.screen.blit(bkgr[k // 5], backgrrect)
        k += 1
        if k == 75: k = 0
        m_buttons['choose_button'].draw()
        m_buttons['settings_button'].draw()
        m_buttons['help_button'].draw()
        m_buttons['exit_button'].draw()
        fps_val(False)
        if error and int(round(time() * 1000)) - error_window_time < 5000:
            error_window.draw()
        user.screen.blit(images['logo'], ((user.size[0] - images['logo'].get_width()) // 2, (user.size[1] - images['logo'].get_height()) // 2 - m_buttons['choose_button'].size[1] * 2))
        pygame.display.update()
        clock.tick(user.fps)
    return False, None, langs['curr_lang'] # main_loop, simulation_name, curr_lang


def choosing_window(start_button=None, sim_content=None, bkgr=None):
    user.screen.fill('#000000')
    choose_cycle = True
    click = img = pre_selected = False
    k = 0 # counter for background
    last_pre_selected = ''
    pre_selected = ''
    text = None
    first_button = list(sim_content)[0]
    text_backgr = pygame.Rect(user.size[0] // 2 + sim_content[first_button][1].size[0] // 2 + sim_content[first_button][1].size[1] / 2, sim_content[first_button][1].size[1] + sim_content[first_button][2].get_height(), sim_content[first_button][2].get_width() + 20 * COEFFICIENT, 5.25 * sim_content[first_button][1].size[1])
    st = 0 # starting point of text generation
    en = 12 # ending point of text generation
    scroll_counter = 0 # added due to division errors
    smooth_counter = 0
    ltime = int(round(time() * 1000)) # to calculate the time delta
    doubleclick = False
    while choose_cycle:
        mx, my = pygame.mouse.get_pos()
        for i in sim_content: # if user clicked on simulation
            if sim_content[i][1].body.collidepoint((mx, my)) and click: # item, button, image, text
                if pre_selected:
                    sim_content[pre_selected][1].select = False
                sim_content[i][1].select = True
                st = 0
                if doubleclick and pre_selected == i:
                    counter = 0
                    for i in sim_content: # reset
                        sim_content[i][1].place = [user.size[0] // 2 - sim_content[first_button][1].size[0] // 2, sim_content[first_button][1].size[1] / 2 + sim_content[first_button][1].size[1] * 1.5 * counter]
                        sim_content[i][1].update()
                        counter += 1
                    sim_content[pre_selected][1].select = False
                    user.screen.fill('#000000')
                    return True, pre_selected
                pre_selected = i
                break
        if (start_button.body.collidepoint((mx, my)) and click) and pre_selected: # if user clicked on start
            counter = 0
            for i in sim_content: # reset
                sim_content[i][1].place = [user.size[0] // 2 - sim_content[first_button][1].size[0] // 2, sim_content[first_button][1].size[1] / 2 + sim_content[first_button][1].size[1] * 1.5 * counter]
                sim_content[i][1].update()
                counter += 1
            sim_content[pre_selected][1].select = False
            user.screen.fill('#000000')
            return True, pre_selected
        click = False
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1: # LB
                    click = True
                    if int(round(time() * 1000)) - ltime < 200:
                        doubleclick = True
                    else:
                        doubleclick = False
                    ltime = int(round(time() * 1000))
                    break
                if event.button == 4: # mouse wheel forward
                    if - sim_content[first_button][1].size[0] // 2 <= mx - user.size[0] // 2 <= sim_content[first_button][1].size[0] // 2: # cursor in buttons' width area 
                        if scroll_counter > 0: # buttons' top limit
                            scroll_counter -= 1
                    elif text_backgr.collidepoint((mx, my)) and text and len(text) > 12 and st > 0: # scrolling the text up
                        st -= 1
                        en -= 1
                elif event.button == 5: # backward
                    if - sim_content[first_button][1].size[0] // 2 < mx - user.size[0] // 2 <= sim_content[first_button][1].size[0] // 2:
                        if scroll_counter < ceil(len(sim_content) - 10): # buttons' bottom limit
                            scroll_counter += 1
                    elif text_backgr.collidepoint((mx, my)) and text and len(text) > 12 and en < len(text): # scrolling the text down
                        st += 1
                        en += 1
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if pre_selected:
                        sim_content[pre_selected][1].select = False
                    counter = 0
                    for i in sim_content: # reset
                        sim_content[i][1].place = [user.size[0] // 2 - sim_content[first_button][1].size[0] // 2, sim_content[first_button][1].size[1] / 2 + sim_content[first_button][1].size[1] * 1.5 * counter]
                        sim_content[i][1].update()
                        counter += 1
                    return True, None
            if event.type == pygame.QUIT:
                return False, None
        pygame.draw.rect(user.screen, '#c8c8c8', text_backgr, 1)
        user.screen.blit(bkgr[k // 5], (0, 0))
        k += 1
        if k == 75: k = 0 # if k out of limit
        if smooth_counter < 6 * scroll_counter: # smooth scrolling down
            for i in sim_content:
                sim_content[i][1].place[1] -= sim_content[first_button][1].size[1] / 4
                sim_content[i][1].update()
            smooth_counter += 1
        elif smooth_counter > 6 * scroll_counter: # up
            for i in sim_content:
                sim_content[i][1].place[1] += sim_content[first_button][1].size[1] / 4
                sim_content[i][1].update()
            smooth_counter -= 1
        for i in sim_content:
            sim_content[i][1].draw()
        if pre_selected:
            if pre_selected != last_pre_selected: # avoidance of repeating
                img = sim_content[pre_selected][2]
                imgrect = (user.size[0] // 2 + sim_content[first_button][1].size[1] / 2 + 10 * COEFFICIENT + sim_content[first_button][1].size[0] // 2, sim_content[first_button][1].size[1] / 2 + 10 * COEFFICIENT)
                img_backg = pygame.Rect(imgrect[0] - 10 * COEFFICIENT, imgrect[1] - 10 * COEFFICIENT, img.get_width() + 20 * COEFFICIENT, img.get_height() + 20 * COEFFICIENT)
                text = sim_content[pre_selected][3]
                if len(text) > 12:
                    en = 12
                else:
                    en = len(text)
                last_pre_selected = pre_selected
            pygame.draw.rect(user.screen, '#c8c8c8', img_backg)
            user.screen.blit(img, imgrect)
            o = 0 # text wrapping
            for i in range(st, en):
                if o < 360 * COEFFICIENT:
                    print_text = sim_info_font.render(text[i], True, '#c8c8c8')
                    user.screen.blit(print_text, (text_backgr.topleft[0], text_backgr.topleft[1] + o))
                    o += 30 * COEFFICIENT
            start_button.draw()
        fps_val(False)
        pygame.display.update()
        clock.tick(user.fps)


def help_window(help_text, bkgr):
    user.screen.fill('#000000')
    help_cycle = True
    k = 0 # counter for background
    backgrrect = (0, 0)
    transparent_surf = pygame.Surface(user.size)
    transparent_surf.set_alpha(196)
    transparent_surf.fill('#000000')
    while help_cycle:
        o = 0
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    return True
            if event.type == pygame.QUIT:
                return False
        if len(bkgr) > 1:
            user.screen.blit(bkgr[k // 5], backgrrect)
            k += 1
            if k == 75: k = 0
        else:
            user.screen.blit(bkgr[0], backgrrect)
            user.screen.blit(transparent_surf, (0, 0))
        for i in range(len(help_text)):
            print_text = help_font.render(help_text[i], True, '#c8c8c8')
            user.screen.blit(print_text, ((user.size[0] // 2 - print_text.get_width() // 2, user.size[1] // 2 - print_text.get_height() // 2 + o)))
            o += 40 * COEFFICIENT
        fps_val(False)
        pygame.display.update()
        clock.tick(user.fps)


def settings_window(langs, menu_buttons, sim_content, text_dict, bkgr):
    user.screen.fill('#000000')
    settings_cycle = True
    click = False
    k = 0 # counter for background
    backgrrect = (0, 0)
    transparent_surf = pygame.Surface(user.size)
    transparent_surf.set_alpha(196)
    transparent_surf.fill('#000000')
    while settings_cycle:
        mx, my = pygame.mouse.get_pos()
        if menu_buttons['lang_button'].body.collidepoint((mx, my)) and click: # switch language
            db = sqlite3.connect('database.db')
            sql = db.cursor()
            for i in range(len(langs['languages'])):
                if langs['languages'][i] == langs['curr_lang']:
                    if i == len(langs) - 1: 
                        langs['curr_lang'] = langs['languages'][0]
                    else:
                        langs['curr_lang'] = langs['languages'][i + 1]
                    break
            for i in sql.execute("SELECT class, name, text FROM {}".format(langs['curr_lang'])): # buttons
                if i[0] == 'button':
                    menu_buttons[i[1]].text = i[2]
                    menu_buttons[i[1]].update()
                elif i[0] == 'info':
                    text = split_by_separator(i[2], 43)
                    text = list(text)
                    try: sim_content[i[1]][3] = text
                    except: continue
                elif i[0] == 'text':
                    text = split_by_separator(i[2], 43, '|')
                    text = list(text)
                    try: text_dict[i[1]] = text
                    except: continue
            db.close()
        click = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # LB
                    click = True
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    return True, langs['curr_lang'], menu_buttons, sim_content, text_dict
            if event.type == pygame.QUIT:
                return False, langs['curr_lang'], menu_buttons, sim_content, text_dict
        if len(bkgr) > 1:
            user.screen.blit(bkgr[k // 5], backgrrect)
            k += 1
            if k == 75: k = 0
        else:
            user.screen.blit(bkgr[0], backgrrect)
            user.screen.blit(transparent_surf, (0, 0))
        menu_buttons['lang_button'].draw()
        menu_buttons['lang_table'].draw()
        fps_val(False)
        pygame.display.update()
        clock.tick(user.fps)


def game_main_menu(langs, menu_buttons, sim_content, text_dict, images, bkgr):
    game_menu_cycle = True
    click = False
    k = 0.7
    switch = False
    transparent_surf = pygame.Surface(user.size)
    transparent_surf.set_alpha(196)
    transparent_surf.fill('#000000')
    menu_buttons['settings_button'].place[1] = user.size[1] // 2 + menu_buttons['settings_button'].size[1] * 3
    menu_buttons['help_button'].place[1] = user.size[1] // 2 + menu_buttons['help_button'].size[1] * 4.5
    menu_buttons['exit_button'].place[1] = user.size[1] // 2 + menu_buttons['exit_button'].size[1] * 6
    for b in menu_buttons.keys():
        menu_buttons[b].update()
    while game_menu_cycle:
        mx, my = pygame.mouse.get_pos()
        if menu_buttons['continue_button'].body.collidepoint((mx, my)) and click:
            menu_buttons['settings_button'].place[1] = user.size[1] // 2 + menu_buttons['settings_button'].size[1] * 1.5
            menu_buttons['help_button'].place[1] = user.size[1] // 2 + menu_buttons['help_button'].size[1] * 3
            menu_buttons['exit_button'].place[1] = user.size[1] // 2 + menu_buttons['exit_button'].size[1] * 4.5
            for b in menu_buttons.keys():
                menu_buttons[b].update()
            return True, langs, False # simulation's cycle, languages, exit from the program
        elif menu_buttons['settings_button'].body.collidepoint((mx, my)) and click:
            game_menu_cycle, langs['curr_lang'], menu_buttons, menu_buttons, text_dict = settings_window(langs, menu_buttons, menu_buttons, text_dict, bkgr)
        elif menu_buttons['help_button'].body.collidepoint((mx, my)) and click:
            game_menu_cycle = help_window(text_dict['help_text'], bkgr)
        elif menu_buttons['exit_button'].body.collidepoint((mx, my)) and click: # exit button
            menu_buttons['settings_button'].place[1] = user.size[1] // 2 + menu_buttons['settings_button'].size[1] * 1.5
            menu_buttons['help_button'].place[1] = user.size[1] // 2 + menu_buttons['help_button'].size[1] * 3
            menu_buttons['exit_button'].place[1] = user.size[1] // 2 + menu_buttons['exit_button'].size[1] * 4.5
            for b in menu_buttons.keys():
                menu_buttons[b].update()
            return False, langs, False
        click = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # LB
                    click = True
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    menu_buttons['settings_button'].place[1] = user.size[1] // 2 + menu_buttons['settings_button'].size[1] * 1.5
                    menu_buttons['help_button'].place[1] = user.size[1] // 2 + menu_buttons['help_button'].size[1] * 3
                    menu_buttons['exit_button'].place[1] = user.size[1] // 2 + menu_buttons['exit_button'].size[1] * 4.5
                    for b in menu_buttons.keys():
                        menu_buttons[b].update()
                    return True, langs, False
            if event.type == pygame.QUIT:
                menu_buttons['settings_button'].place[1] = user.size[1] // 2 + menu_buttons['settings_button'].size[1] * 1.5
                menu_buttons['help_button'].place[1] = user.size[1] // 2 + menu_buttons['help_button'].size[1] * 3
                menu_buttons['exit_button'].place[1] = user.size[1] // 2 + menu_buttons['exit_button'].size[1] * 4.5
                for b in menu_buttons.keys():
                    menu_buttons[b].update()
                return False, langs, True
        user.screen.blit(bkgr[0], (0, 0))
        user.screen.blit(transparent_surf, (0, 0))
        pygame.draw.rect(user.screen, (200 * k, 200 * k, 200 * k), (user.size[0] // 2 - 30 * COEFFICIENT, user.size[1] // 2 - 3 * user.size[1] / 31, 20 * COEFFICIENT, 2 * user.size[1] / 31))
        pygame.draw.rect(user.screen, (200 * k, 200 * k, 200 * k), (user.size[0] // 2 + 10 * COEFFICIENT, user.size[1] // 2 - 3 * user.size[1] / 31, 20 * COEFFICIENT, 2 * user.size[1] / 31))
        if k < 1 and not(switch):
            k += 0.01
        elif k > 0.7:
            k -= 0.01
            switch = True
        else:
            switch = False
        menu_buttons['continue_button'].draw()
        menu_buttons['save_button'].draw()
        menu_buttons['settings_button'].draw()
        menu_buttons['help_button'].draw()
        menu_buttons['exit_button'].draw()
        fps_val(False)
        pygame.display.update()
        clock.tick(user.fps)
    menu_buttons['settings_button'].place[1] = user.size[1] // 2 + menu_buttons['settings_button'].size[1] * 1.5
    menu_buttons['help_button'].place[1] = user.size[1] // 2 + menu_buttons['help_button'].size[1] * 3
    menu_buttons['exit_button'].place[1] = user.size[1] // 2 + menu_buttons['exit_button'].size[1] * 4.5
    for b in menu_buttons.keys():
        menu_buttons[b].update()
    return False, langs, True


def mode_elements(selected_obj, selected_obj_velocity, maximum, zoom, COEFFICIENT, movement):
    """This function draws all advanced mode graphic items."""
    pygame.draw.line(user.screen, '#555555', (30 * COEFFICIENT, user.size[1] - 30 * COEFFICIENT), (30 * COEFFICIENT + 199, user.size[1] - 30 * COEFFICIENT), 1) # scale line
    pygame.draw.line(user.screen, '#555555', (30 * COEFFICIENT, user.size[1] - 20 * COEFFICIENT), (30 * COEFFICIENT, user.size[1] - 40 * COEFFICIENT), 1)
    pygame.draw.line(user.screen, '#555555', (30 * COEFFICIENT + 99, user.size[1] - 20 * COEFFICIENT), (30 * COEFFICIENT + 99, user.size[1] - 40 * COEFFICIENT), 1)
    pygame.draw.line(user.screen, '#555555', (30 * COEFFICIENT + 199, user.size[1] - 20 * COEFFICIENT), (30 * COEFFICIENT + 199, user.size[1] - 40 * COEFFICIENT), 1)
    user.screen.blit(obj_info_font.render("In 100px {} km.".format(round(10**5 / zoom, 3)), True, '#555555'), (30 * COEFFICIENT, user.size[1] - 60 * COEFFICIENT))
    user.screen.blit(obj_info_font.render('(0, 0)', True, '#444444'), (movement[0]* zoom + 6 * COEFFICIENT, movement[1]* zoom - 24 * COEFFICIENT))
    pygame.draw.circle(user.screen, '#444444', (movement[0] * zoom, movement[1] * zoom), 4)
    if selected_obj != None and len(selected_obj_velocity) > 2: # graph
        pygame.draw.aalines(user.screen, '#c80000', False, [i[:2] for i in selected_obj_velocity], 2)
        pygame.draw.line(user.screen, '#666666', (user.size[0] - 350 * COEFFICIENT, user.size[1] - 35 * COEFFICIENT), (user.size[0] - 350 * COEFFICIENT, user.size[1] - 235 * COEFFICIENT), 1)
        pygame.draw.line(user.screen, '#555555', (user.size[0] - 350 * COEFFICIENT, user.size[1] - 235 * COEFFICIENT), (user.size[0] - 355 * COEFFICIENT, user.size[1] - 235 * COEFFICIENT), 1)
        pygame.draw.line(user.screen, '#555555', (user.size[0] - 350 * COEFFICIENT, user.size[1] - 210 * COEFFICIENT), (user.size[0] - 355 * COEFFICIENT, user.size[1] - 210 * COEFFICIENT), 1)
        pygame.draw.line(user.screen, '#555555', (user.size[0] - 350 * COEFFICIENT, user.size[1] - 185 * COEFFICIENT), (user.size[0] - 355 * COEFFICIENT, user.size[1] - 185 * COEFFICIENT), 1)
        pygame.draw.line(user.screen, '#555555', (user.size[0] - 350 * COEFFICIENT, user.size[1] - 160 * COEFFICIENT), (user.size[0] - 355 * COEFFICIENT, user.size[1] - 160 * COEFFICIENT), 1)
        pygame.draw.line(user.screen, '#555555', (user.size[0] - 350 * COEFFICIENT, user.size[1] - 135 * COEFFICIENT), (user.size[0] - 355 * COEFFICIENT, user.size[1] - 135 * COEFFICIENT), 1)
        pygame.draw.line(user.screen, '#555555', (user.size[0] - 350 * COEFFICIENT, user.size[1] - 110 * COEFFICIENT), (user.size[0] - 355 * COEFFICIENT, user.size[1] - 110 * COEFFICIENT), 1)
        pygame.draw.line(user.screen, '#555555', (user.size[0] - 350 * COEFFICIENT, user.size[1] - 85 * COEFFICIENT), (user.size[0] - 355 * COEFFICIENT, user.size[1] - 85 * COEFFICIENT), 1)
        pygame.draw.line(user.screen, '#555555', (user.size[0] - 350 * COEFFICIENT, user.size[1] - 60 * COEFFICIENT), (user.size[0] - 355 * COEFFICIENT, user.size[1] - 60 * COEFFICIENT), 1)
        pygame.draw.line(user.screen, '#555555', (user.size[0] - 355 * COEFFICIENT, user.size[1] - 35 * COEFFICIENT), (user.size[0] - 55 * COEFFICIENT, user.size[1] - 35 * COEFFICIENT), 1)
        pygame.draw.line(user.screen, '#555555', (user.size[0] - 55 * COEFFICIENT, user.size[1] - 35 * COEFFICIENT), (user.size[0] - 55 * COEFFICIENT, user.size[1] - 30 * COEFFICIENT), 1)
        velocity_graph_text = obj_info_font.render(str(round(maximum / 1000, 3)) + " km/s", True, '#c8c8c8')
        user.screen.blit(velocity_graph_text, (user.size[0] - 370 * COEFFICIENT - velocity_graph_text.get_width(), user.size[1] - 235 * COEFFICIENT - velocity_graph_text.get_height() // 2))
        velocity_graph_text = obj_info_font.render("10 sec", True, '#c8c8c8')
        user.screen.blit(velocity_graph_text, (user.size[0] - 50 * COEFFICIENT - velocity_graph_text.get_width() // 2, user.size[1] - 20 * COEFFICIENT - velocity_graph_text.get_height() // 2))


def simulation_loop(space_objects, simulation_name, images, menu_buttons, sim_content, text_dict, langs, COEFFICIENT, DT, G, DIST_COEFF):
    zoom = 1.0
    movement_speed, movement = 4, [0, 0]
    movement_obj = [0, 0] # object created to approach the center 
    selected_obj_velocity = [] # velocity dataset
    maximum = 100 # maximum value in a time interval 
    velocity_add_timer = 0 # time interval for adding data to the graph
    moving_right = moving_left = moving_up = moving_down = shift_pressed = False
    sim_cycle = True
    pause = mode = False
    mx = my = None
    img = None
    selected_obj = None
    if len(space_objects) > 1000:
        pygame.draw.rect(user.screen, '#005ffe', (user.size[0] // 2 - 500 * COEFFICIENT, user.size[1] // 2 - user.size[1] / 31, 1000 * COEFFICIENT, user.size[1] / 31))
        pygame.display.update()
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
                    screenshot_rect = pygame.Rect(0, 0, user.size[0], user.size[1])
                    screenshot = [display_surf.subsurface(screenshot_rect)] # screenshot of last objects' posotion
                    sim_cycle, langs, exit_from_prog = game_main_menu(langs, menu_buttons, sim_content, text_dict, images, screenshot)
                    if not(sim_cycle): 
                        space_objects = []
                        if exit_from_prog:
                            return False, langs
                        else:
                            return True, langs
                if event.key == K_e:
                    mode = not(mode)
                if event.key == K_LSHIFT:
                    shift_pressed = True
                if event.key == K_r:
                    user.screen.fill('#000000')
                    space_objects = []
                    space_objects = init_simulation(space_objects, simulation_name, images['objects'], COEFFICIENT)
                    [space_objects[i].update(zoom) for i in range(len(space_objects))]
                if event.key == K_0:
                    movement = [0, 0]
                    zoom = 1
                    [space_objects[i].update(zoom) for i in range(len(space_objects))]
                if event.key == K_p:
                    pause = not(pause)
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1: # LBM
                    mx, my = pygame.mouse.get_pos()
                    if mode:
                        for o in range(len(space_objects)):
                            pos_on_display = ((space_objects[o].x * DIST_COEFF + movement[0]) * zoom, (space_objects[o].y * DIST_COEFF + movement[1]) * zoom) # position of object on the display
                            r_on_display = space_objects[o].r * zoom * DIST_COEFF # radius of object on the display
                            if - r_on_display < mx - pos_on_display[0] < r_on_display and - r_on_display < my - pos_on_display[1] < r_on_display:
                                if selected_obj == o:
                                    movement_obj[0] = - space_objects[selected_obj].x * DIST_COEFF
                                    movement_obj[1] = - space_objects[selected_obj].y * DIST_COEFF
                                    selected_obj = None
                                    selected_obj_velocity = []
                                else:
                                    selected_obj = o
                                break
                    elif not(shift_pressed):
                        img = images['objects']['star_img']
                        aStar = obj(int(mx / DIST_COEFF / zoom - movement[0] / DIST_COEFF), int(my / DIST_COEFF / zoom - movement[1] / DIST_COEFF), images['objects']['star_img'], 16e+6, 1e+22)
                        aStar.transformed_img = pygame.transform.scale(img, (int(img.get_width() * zoom), int(img.get_height() * zoom)))
                        space_objects.append(aStar)
                if event.button == 4: # mouse wheel forward
                    zoom += 0.005 + 0.05 * zoom
                    zoom = round(zoom, 3)
                    [space_objects[i].update(zoom) for i in range(len(space_objects))]
                elif event.button == 5: # backward
                    if zoom > 0.005:
                        zoom -= (0.005 + 0.05 * zoom)
                        zoom = round(zoom, 3)
                        [space_objects[i].update(zoom) for i in range(len(space_objects))]
            if event.type == MOUSEBUTTONUP:
                if event.button == 1 and mx and shift_pressed and not(mode):
                    img = images['objects']['star_img']
                    aStar = obj(int(mx / DIST_COEFF / zoom - movement[0] / DIST_COEFF), int(my / DIST_COEFF / zoom - movement[1] / DIST_COEFF), images['objects']['star_img'], 16e+6, 1e+22, (pygame.mouse.get_pos()[0] - mx) * 10, (pygame.mouse.get_pos()[1] - my) * 10)
                    aStar.transformed_img = pygame.transform.scale(img, (int(img.get_width() * zoom), int(img.get_height() * zoom)))
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
                if event.key == K_LSHIFT:
                    shift_pressed = False
            if event.type == pygame.QUIT:
                return False, langs
        if moving_up:
            movement_obj[1] += movement_speed / zoom 
        if moving_down:
            movement_obj[1] -= movement_speed / zoom
        if moving_left:
            movement_obj[0] += movement_speed / zoom
        if moving_right:
            movement_obj[0] -= movement_speed / zoom
        display_surf.fill('#000000')
        space_objects = step(space_objects, pause, DT, G)
        if selected_obj != None: # camera follows the selected object
            if not(pause):
                movement[0] = - space_objects[selected_obj].x * DIST_COEFF + (user.size[0] // 2) / zoom
                movement[1] = - space_objects[selected_obj].y * DIST_COEFF + (user.size[1] // 2) / zoom
                if len(selected_obj_velocity) >= 200:
                    selected_obj_velocity.pop(0)
                    for t in range(len(selected_obj_velocity)):
                        selected_obj_velocity[t][0] -= 1.5 * COEFFICIENT
                if int(round(time() * 1000)) - velocity_add_timer > 50 or velocity_add_timer == 0: # addition velocity data 
                    velocity_add_timer = int(round(time() * 1000))
                    selected_obj_velocity.append([user.size[0] - 350 * COEFFICIENT + len(selected_obj_velocity) * 1.5 * COEFFICIENT, user.size[1] - 35 * COEFFICIENT - 200 * hypot(space_objects[selected_obj].vx, space_objects[selected_obj].vy) / maximum * COEFFICIENT, hypot(space_objects[selected_obj].vx, space_objects[selected_obj].vy)]) # [X on display, Y on display, velocity]
                    if max(selected_obj_velocity, key=lambda x: x[2])[2] > 0 and max(selected_obj_velocity, key=lambda x: x[2])[2] != maximum:
                        maximum = max(selected_obj_velocity, key=lambda x: x[2])[2]
                        for t in range(len(selected_obj_velocity)):
                            selected_obj_velocity[t][1] = user.size[1] - 35 * COEFFICIENT - 200 * selected_obj_velocity[t][2] / maximum * COEFFICIENT
        else: # camera follows the movement_obj
            movement[0] = movement_obj[0] + (user.size[0] // 2) / zoom
            movement[1] = movement_obj[1] + (user.size[1] // 2) / zoom
        [space_objects[i].draw(zoom, movement, mode, COEFFICIENT, DIST_COEFF) for i in range(len(space_objects))] # drawing all objects
        user.screen.blit(display_surf, (0, 0))
        if mode:
            mode_elements(selected_obj, selected_obj_velocity, maximum, zoom, COEFFICIENT, movement)
        if len(space_objects) > 0:
            fps_val(True, zoom, movement, space_objects[-1], len(space_objects), DT, DIST_COEFF)
        else:
            fps_val(True, zoom, movement, None, 0, DT, DIST_COEFF)
        pygame.display.update()
        clock.tick(user.fps)


if __name__ == '__main__':
    display_surf = pygame.Surface((user.size[0], user.size[1]))
    display_surf.set_alpha(None)
    simulations_content, menu_buttons, images, languages, text_dict = init_content(COEFFICIENT)
    simulation_name = ''
    space_objects = ['', '']
    main_loop = True
    error = None
    clock = pygame.time.Clock()
    while main_loop:
        main_loop, simulation_name, languages['curr_lang'] = main_menu(error, simulations_content, languages, menu_buttons, text_dict, images, COEFFICIENT)
        if simulation_name:
            space_objects = init_simulation(space_objects, simulation_name, images['objects'], COEFFICIENT)
            if space_objects[0] != 'error':
                main_loop, languages = simulation_loop(space_objects, simulation_name, images, menu_buttons, simulations_content, text_dict, languages, COEFFICIENT, DT, G, DIST_COEFF)
                simulation_name = ''
                space_objects = ['', '']
                error = None
            else:
                error = space_objects[1]
    
    if languages['curr_lang'] in languages['languages']:
        db = sqlite3.connect('database.db')
        sql = db.cursor()
        sql.execute("UPDATE settings SET language = '{}' WHERE user = 'user01'".format(languages['curr_lang']))
        db.commit()
        db.close()
    pygame.quit()
    exit('Exit')
