import pygame
from pygame.locals import *
from time import time, sleep, strftime, strptime, ctime
from math import cos, sin, asin, pi, sqrt, degrees, atan2, radians, ceil
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
if user.size[0] / 1920 < user.size[1] / 1080:
    COEFFICIENT = user.size[0] / 1920
else:
    COEFFICIENT = user.size[1] / 1080
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
        self.x = x
        self.y = y
        self.r = r
        self.m = m
        self.img = img
        self.transformed_img = img
        self.vx = vx
        self.vy = vy
        self.coll = False # collision state (True if collision happened)
    def update(self, zoom: float):
        self.transformed_img = pygame.transform.scale(self.img, (int(self.img.get_width() * zoom), int(self.img.get_height() * zoom)))
    def draw(self, zoom: float, movement: list, mode: bool, COEFFICIENT: float):
        if mode:
            x_coord = (self.x + movement[0] + 10 + self.r) * zoom # coordinates of the text 
            y_coord = (self.y + movement[1] - self.r) * zoom
            if (self.vy != 0 or self.vx != 0):
                sin_ = self.vy / ((self.vy * self.vy + self.vx * self.vx) ** 0.5)
                cos_ = self.vx / ((self.vy * self.vy + self.vx * self.vx) ** 0.5)
                start = [(self.x + movement[0]) * zoom, (self.y + movement[1]) * zoom] # start point of line
                end = [(self.x + movement[0] + 100 * cos_) * zoom, (self.y + movement[1] + 100 * sin_) * zoom] # end point of line
                pygame.draw.line(display_surf, '#c80000', start, end, 2) # direction line
                rotation = degrees(atan2(start[1] - end[1], end[0] - start[0])) + 90
                pygame.draw.polygon(display_surf, '#c80000', ((end[0] + (10 * sin(radians(rotation))) * zoom, end[1] + (10 * cos(radians(rotation))) * zoom), (end[0] + (5 * sin(radians(rotation - 120))) * zoom, end[1] + (5 * cos(radians(rotation - 120))) * zoom), (end[0] + (5 * sin(radians(rotation + 120))) * zoom, end[1] + (5 * cos(radians(rotation + 120))) * zoom))) # arrowhead
            display_surf.blit(obj_info_font.render("vx, vy: {}, {}".format(round(self.vx, 3), round(self.vy, 3)), True, '#c8c8c8'), (x_coord, y_coord - 26 * COEFFICIENT))
            display_surf.blit(obj_info_font.render("m: " + str(self.m), True, '#c8c8c8'), (x_coord, y_coord - 10 * COEFFICIENT))
            display_surf.blit(obj_info_font.render("coll: " + str(self.coll), True, '#c8c8c8'), (x_coord, y_coord + 6 * COEFFICIENT))
        display_surf.blit(self.transformed_img, \
            # x:
            (int((self.x + movement[0] - self.r) * zoom), \
            # y:
            int((self.y + movement[1] - self.r) * zoom)))


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
            aStar = obj(float(sim[i][0]), float(sim[i][1]), images[sim[i][2]], float(sim[i][3]), float(sim[i][4]))
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
    """Creates all main dicts, lists and getting current language"""
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
                text = sql.execute("SELECT class, name, text FROM '{}' WHERE class = 'info' and name = '{}'".format(languages['curr_lang'], item)).fetchone()[2]
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
    for item in os.listdir('data'):
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
def fps_val(game=True, zoom_=1, movement=[0, 0]):
    """Returns value of fraps per second"""
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


def step(space_objects, pause=False, dt=1.0, G=1.0):
    if pause: return None
    for i in range(len(space_objects)): # current
        i_obj = space_objects[i]
        for j in range(len(space_objects)): # another
            if i == j or i_obj.coll or space_objects[j].coll: continue
            j_obj = space_objects[j]
            dx = j_obj.x - i_obj.x
            dy = j_obj.y - i_obj.y
            r = dx * dx + dy * dy # R^2
            if r > (j_obj.r + i_obj.r) * (j_obj.r + i_obj.r):
                a = G * j_obj.m / r
                r = sqrt(r) # R
                if r < 0.01: r = 0.01
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
                space_objects[i].coll = True
                break
        else:
            space_objects[i].coll = False
    for i in range(len(space_objects)):
        space_objects[i].x += space_objects[i].vx * dt
        space_objects[i].y += space_objects[i].vy * dt

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
                pre_selected = i
                sim_content[i][1].select = True
                st = 0
                if doubleclick:
                    counter = 0
                    for i in sim_content: # reset
                        sim_content[i][1].place = [user.size[0] // 2 - sim_content[first_button][1].size[0] // 2, sim_content[first_button][1].size[1] / 2 + sim_content[first_button][1].size[1] * 1.5 * counter]
                        sim_content[i][1].update()
                        counter += 1
                    sim_content[pre_selected][1].select = False
                    user.screen.fill('#000000')
                    return True, pre_selected
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
    while help_cycle:
        o = 0
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    return True
            if event.type == pygame.QUIT:
                return False
        user.screen.blit(bkgr[k // 5], backgrrect)
        k += 1
        if k == 75: k = 0
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
                    sim_content[i[1]][3] = text
                elif i[0] == 'text':
                    text = split_by_separator(i[2], 43, '|')
                    text = list(text)
                    text_dict[i[1]] = text
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
        user.screen.blit(bkgr[k // 5], backgrrect)
        k += 1
        if k == 75: k = 0
        menu_buttons['lang_button'].draw()
        menu_buttons['lang_table'].draw()
        fps_val(False)
        pygame.display.update()
        clock.tick(user.fps)


def simulation_loop(space_objects, simulation_name, images, COEFFICIENT, dt, G):
    zoom = 1.0
    movement_speed, movement = 4, [0, 0]
    moving_right = moving_left = moving_up = moving_down = shift_pressed = False
    sim_cycle = True
    pause = mode = False
    mx, my = (0, 0)
    if len(space_objects) > 500:
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
                    return True
                if event.key == K_e:
                    if not(mode): mode = True
                    else: mode = False
                if event.key == K_LSHIFT:
                    shift_pressed = True
                if event.key == K_r:
                    user.screen.fill('#000000')
                    space_objects = []
                    space_objects = init_simulation(space_objects, simulation_name, images['objects'], COEFFICIENT)
                if event.key == K_0:
                    movement = [0, 0]
                if event.key == K_p:
                    if not(pause):
                        pause = True
                    else:
                        pause = False
            
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1: # LBM
                    mx, my = pygame.mouse.get_pos()
                    if not(shift_pressed):
                        aStar = obj(int(mx / zoom - movement[0]), int(my / zoom - movement[1]), images['objects']['star_img'], 16.0, 1.0)
                        space_objects.append(aStar)
                if event.button == 4: # mouse wheel forward
                    zoom += 0.1
                    if zoom > 4:
                        zoom += 0.1
                    zoom = round(zoom, 1)
                    [space_objects[i].update(zoom) for i in range(len(space_objects))]
                elif event.button == 5: # backward
                    if zoom > 0.1:
                        zoom -= 0.1
                        zoom = round(zoom, 1)
                        [space_objects[i].update(zoom) for i in range(len(space_objects))]
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
            if event.type == MOUSEBUTTONUP:
                if event.button == 1 and shift_pressed and abs(pygame.mouse.get_pos()[0] - mx) > 0.1 and abs(pygame.mouse.get_pos()[1] - my) > 0.1:
                    aStar = obj(int(mx / zoom - movement[0]), int(my / zoom - movement[1]), images['objects']['star_img'], 16.0, 1.0, pygame.mouse.get_pos()[0] - mx, pygame.mouse.get_pos()[1] - my)
                    space_objects.append(aStar)
            if event.type == pygame.QUIT:
                return False
        if moving_up:
            movement[1] += movement_speed / zoom
        if moving_down:
            movement[1] -= movement_speed / zoom
        if moving_left:
            movement[0] += movement_speed / zoom
        if moving_right:
            movement[0] -= movement_speed / zoom
        display_surf.fill('#000000')
        step(space_objects, pause, dt, G)
        [space_objects[i].draw(zoom, movement, mode, COEFFICIENT) for i in range(len(space_objects))] # drawing all objects
        user.screen.blit(display_surf, (0, 0))
        fps_val(zoom_=zoom, movement=movement)
        pygame.display.update()
        clock.tick(user.fps)


if __name__ == '__main__':
    display_surf = pygame.Surface((user.size[0], user.size[1]))
    display_surf.set_alpha(None)
    G = 1000.0 # real value = 6.67430e-11. You will need to use decimal or waiting for updates to calculate that
    SPEED = 1 # simulation speed
    dt = (1 / user.fps) * SPEED # time step for objects
    
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
                main_loop = simulation_loop(space_objects, simulation_name, images, COEFFICIENT, dt, G)
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
