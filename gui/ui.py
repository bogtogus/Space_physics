import pygame
from pygame.locals import *
from time import time, strftime, localtime
from constants import *
from tech import engine, tools, content, simulation
from tech.button import button


def run():
    simulations_content, menu_buttons, images, languages, text_dict = content.init_content()
    simulation_name = None
    space_objects = ['', '']
    main_loop = True
    error = None
    while main_loop:
        main_loop, simulation_name, user.language = main_menu(
            error=error, simulations_content=simulations_content, 
            languages=languages, menu_buttons=menu_buttons, 
            text_dict=text_dict, images=images, user=user, 
            COEFFICIENT=COEFFICIENT)
        if simulation_name:
            space_objects = simulation.initialise(
                name=simulation_name,
                images=images['objects'],
                win_size=user.size,
                display_surf=display_surf,
                HOME_DIR=HOME_DIR)
            if space_objects[0] != 'error':
                main_loop, languages = simulation_loop(
                    space_objects=space_objects, 
                    simulation_name=simulation_name, 
                    images=images, menu_buttons=menu_buttons, 
                    simulations_content=simulations_content, 
                    text_dict=text_dict, languages=languages, 
                    user=user, COEFFICIENT=COEFFICIENT, 
                    DT=DT, G=G, DIST_COEFF=DIST_COEFF)
                simulation_name = error = None
                space_objects = ['', '']
            else:
                error = space_objects[1]
    tools.db_change_language(user=user, languages=languages)
    pygame.quit()


def fps_val(
        game=True,
        zoom=1,
        movement=[0, 0],
        space_object=None,
        obj_amount=0,
        simulation_time=0,
        DIST_COEFF=1):
    """This function draws value of fraps per second and other stuff."""
    global fps, frames, cur_time
    if int(round(time() * 1000)) - cur_time > 1000:
        fps = frames
        frames = 0
        cur_time = int(round(time() * 1000))
    if game:
        if space_object:
            x, y = (space_object.x, space_object.y)
            data = '{} fps, {} obj, zoom: {}, [last object position]: {} px, Real: {} m*10^6'.format(
                    fps, obj_amount, zoom,
                    (int((x * DIST_COEFF + movement[0]) * zoom), 
                    int((y * DIST_COEFF + movement[1]) * zoom)), 
                    (int(x * DIST_COEFF), int(y * DIST_COEFF)))
        else:
            data = '{} fps, {} obj, zoom: {}'.format(fps, 0, zoom)
        data = DEAFULT_FONT.render(data, True, '#c8c8c8')
        user.screen.blit(DEAFULT_FONT.render(str(strftime('%x %X', localtime(
            simulation_time))), True, '#c8c8c8'), (0, 1.5 * data.get_height()))
    else:
        data = str(fps) + ' fps'
        data = DEAFULT_FONT.render(data, True, '#c8c8c8')
    user.screen.blit(data, (0, 0))
    frames += 1


def main_menu(
        error=None,
        simulations_content=None,
        languages=None,
        menu_buttons=None,
        text_dict=None,
        images=None,
        user=None,
        COEFFICIENT=1.0):
    user.screen.fill('#000000')
    bkgr = images['background']
    menu_cycle = True
    click = False
    k = 0  # counter for background
    selected_sim = None
    backgrrect = (0, 0)
    if error:
        error_text = DEAFULT_FONT.render(error, True, '#ee1111')
        error_window = button(
            place=[35 * COEFFICIENT,
                   user.size[1] - 75 * COEFFICIENT],
            size=(error_text.get_width() + 70 * COEFFICIENT,
                  50 * COEFFICIENT),
            color='#990000',
            button_text=error,
            font_size=round(24 * COEFFICIENT),
            font_color='#dddddd',
            HOME_DIR=HOME_DIR)
        error_window_timer = int(round(time() * 1000))
    while menu_cycle:
        mx, my = pygame.mouse.get_pos()
        if menu_buttons['choose_button'].body.collidepoint((mx, my)) and click:
            menu_cycle, selected_sim = choosing_window(
                menu_buttons['start_button'], simulations_content, bkgr, user, COEFFICIENT)
            if selected_sim:
                # main_loop, simulation_name, user.language
                return True, selected_sim, user.language
            elif not(menu_cycle):  # if user closed the window
                break
        elif menu_buttons['settings_button'].body.collidepoint((mx, my)) and click:
            menu_cycle, user.language, menu_buttons, simulations_content, text_dict = settings_window(
                languages, menu_buttons, simulations_content, text_dict, bkgr, user, COEFFICIENT)
        elif menu_buttons['help_button'].body.collidepoint((mx, my)) and click:
            menu_cycle = help_window(
                text_dict['help_text'], bkgr, user, COEFFICIENT)
        elif menu_buttons['exit_button'].body.collidepoint((mx, my)) and click:
            break
        click = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # LB
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
        if k == len(bkgr) * 5:
            k = 0
        menu_buttons['choose_button'].draw(user=user)
        menu_buttons['settings_button'].draw(user=user)
        menu_buttons['help_button'].draw(user=user)
        menu_buttons['exit_button'].draw(user=user)
        fps_val(False)
        if error and int(round(time() * 1000)) - error_window_timer < 5000:
            error_window.draw(user=user)
        user.screen.blit(
            images['logo'],
            ((user.size[0] - images['logo'].get_width()) // 2,
             (user.size[1] - images['logo'].get_height()) // 2 -
             menu_buttons['choose_button'].size[1] * 2))
        pygame.display.update()
        clock.tick(user.fps)
    return False, None, user.language  # main_loop, simulation_name, user.language


def reset_sim_buttons(simulations_content=None, 
                      pre_selected=None):
    counter = 0
    first_button = list(simulations_content)[0]
    width = simulations_content[first_button][1].size[0]
    height = simulations_content[first_button][1].size[1]
    for i in simulations_content:  # reset buttons' place
        simulations_content[i][1].place = [
            (user.size[0] - width) // 2,
            height / 2 + height * 1.5 * counter]
        simulations_content[i][1].update()
        counter += 1
    if pre_selected != '':
        simulations_content[pre_selected][1].select = False


def choosing_window(
        start_button=None,
        simulations_content=None,
        bkgr=None,
        user=None,
        COEFFICIENT=1.0):
    user.screen.fill('#000000')
    choose_cycle = True
    click = img = pre_selected = False
    k = 0  # counter for background
    last_pre_selected = ''
    pre_selected = ''
    text = None
    first_button = list(simulations_content)[0]
    text_backgr = pygame.Rect(
        ((user.size[0] +
          simulations_content[first_button][1].size[0] +
          simulations_content[first_button][1].size[1]) // 2),
        simulations_content[first_button][1].size[1] +
        simulations_content[first_button][2].get_height(),
        simulations_content[first_button][2].get_width() + 20 * COEFFICIENT, 
        5.25 * simulations_content[first_button][1].size[1])
    st = 0  # starting point of text generation
    en = 12  # ending point of text generation
    scroll_counter = 0  # added due to division errors
    smooth_counter = 0
    ltime = int(round(time() * 1000))  # to calculate the time delta
    doubleclick = False
    while choose_cycle:
        mx, my = pygame.mouse.get_pos()
        for i in simulations_content:  # if user clicked on simulation
            if simulations_content[i][1].body.collidepoint(
                    (mx, my)) and click:
                if pre_selected:
                    simulations_content[pre_selected][1].select = False
                simulations_content[i][1].select = True
                st = 0
                if doubleclick and pre_selected == i:
                    reset_sim_buttons(simulations_content=simulations_content, 
                                      pre_selected=pre_selected)
                    user.screen.fill('#000000')
                    return True, pre_selected  # menu_cycle, selected_sim
                pre_selected = i
                break
        if (start_button.body.collidepoint((mx, my))
                and click) and pre_selected:  # if user clicked on start
            reset_sim_buttons(simulations_content=simulations_content, 
                              pre_selected=pre_selected)
            user.screen.fill('#000000')
            return True, pre_selected  # menu_cycle, selected_sim
        click = False
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # LB
                    click = True
                    if int(round(time() * 1000)) - ltime < 200:
                        doubleclick = True
                    else:
                        doubleclick = False
                    ltime = int(round(time() * 1000))
                    break
                if event.button == 4:  # mouse wheel forward
                    if - simulations_content[first_button][1].size[0] <= 2 * mx - \
                            user.size[0] <= simulations_content[first_button][1].size[0]:  
                        # cursor in buttons' width area
                        if scroll_counter > 0:  # buttons' top limit
                            scroll_counter -= 1
                    # scrolling the text up
                    elif text_backgr.collidepoint((mx, my)) and text and len(text) > 12 and st > 0:
                        st -= 1
                        en -= 1
                elif event.button == 5:  # backward
                    if - simulations_content[first_button][1].size[0] <= 2 * mx - \
                            user.size[0] <= simulations_content[first_button][1].size[0]:
                        if scroll_counter < ceil(
                                len(simulations_content) - 10):  # buttons' bottom limit
                            scroll_counter += 1
                    # scrolling the text down
                    elif text_backgr.collidepoint((mx, my)) and \
                            text and len(text) > 12 and en < len(text):
                        st += 1
                        en += 1
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    reset_sim_buttons(simulations_content=simulations_content, 
                                      pre_selected=pre_selected)
                    user.screen.fill('#000000')
                    return True, None  # menu_cycle, selected_sim
            if event.type == pygame.QUIT:
                return False, None  # menu_cycle, selected_sim
        # smooth scrolling down. One signal from the mouse wheel moves the
        # buttons by 1.5 of their height.
        if smooth_counter < 6 * scroll_counter:
            for i in simulations_content:
                simulations_content[i][1].place[1] -= simulations_content[first_button][1].size[1] / 4
                simulations_content[i][1].update()
            smooth_counter += 1
        elif smooth_counter > 6 * scroll_counter:  # up
            for i in simulations_content:
                simulations_content[i][1].place[1] += simulations_content[first_button][1].size[1] / 4
                simulations_content[i][1].update()
            smooth_counter -= 1
        pygame.draw.rect(user.screen, '#c8c8c8', text_backgr, 1)  # text rectangle
        user.screen.blit(bkgr[k // 5], (0, 0))
        k += 1
        if k == len(bkgr) * 5:
            k = 0  # if k out of limit
        for i in simulations_content:
            simulations_content[i][1].draw(user=user)
        if pre_selected:
            if pre_selected != last_pre_selected:  # avoidance of repeating
                img = simulations_content[pre_selected][2]
                imgrect = (
                    ((user.size[0] +
                      simulations_content[first_button][1].size[1] +
                      simulations_content[first_button][1].size[0]) //
                     2 + 10 * COEFFICIENT),
                    (simulations_content[first_button][1].size[1] / 2 + 
                     10 * COEFFICIENT))
                img_backg = pygame.Rect(
                    imgrect[0] - 10 * COEFFICIENT,
                    imgrect[1] - 10 * COEFFICIENT,
                    img.get_width() + 20 * COEFFICIENT,
                    img.get_height() + 20 * COEFFICIENT)
                text = simulations_content[pre_selected][3]
                if len(text) > 12:
                    en = 12
                else:
                    en = len(text)
                last_pre_selected = pre_selected
            pygame.draw.rect(user.screen, '#c8c8c8', img_backg)
            user.screen.blit(img, imgrect)
            o = 0  # text wrapping
            for i in range(st, en):
                if o < 360 * COEFFICIENT:
                    print_text = SIM_INFO_FONT.render(text[i], True, '#c8c8c8')
                    user.screen.blit(
                        print_text, (text_backgr.topleft[0], text_backgr.topleft[1] + o))
                    o += 30 * COEFFICIENT
            start_button.draw(user=user)
        fps_val(False)
        pygame.display.update()
        clock.tick(user.fps)


def help_window(
        help_text=None,
        bkgr=None,
        user=None,
        COEFFICIENT=1.0):
    help_cycle = True
    k = 0  # counter for background
    backgrrect = (0, 0)
    user.screen.fill('#000000')
    transparent_surf = pygame.Surface(user.size)
    transparent_surf.set_alpha(196)
    transparent_surf.fill('#000000')
    while help_cycle:
        o = 0
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    return True  # menu_cycle
            if event.type == pygame.QUIT:
                return False
        if isinstance(bkgr, list):
            user.screen.blit(bkgr[k // 5], backgrrect)
            k += 1
            if k == len(bkgr) * 5:
                k = 0
        else:  # if help window is launched from the simulation
            user.screen.blit(bkgr, backgrrect)
            user.screen.blit(transparent_surf, (0, 0))
        for i in range(len(help_text)):
            print_text = HELP_FONT.render(help_text[i], True, '#c8c8c8')
            user.screen.blit(
                print_text,
                (((user.size[0] - print_text.get_width()) // 2,
                  (user.size[1] - print_text.get_height()) // 2 + o)))
            o += 40 * COEFFICIENT
        fps_val(False)
        pygame.display.update()
        clock.tick(user.fps)


def settings_window(
        languages=None,
        menu_buttons=None,
        simulations_content=None,
        text_dict=None,
        bkgr=None,
        user=None,
        COEFFICIENT=1.0):
    settings_cycle = True
    click = False
    k = 0  # counter for background
    backgrrect = (0, 0)
    user.screen.fill('#000000')
    transparent_surf = pygame.Surface(user.size)
    transparent_surf.set_alpha(196)
    transparent_surf.fill('#000000')
    while settings_cycle:
        mx, my = pygame.mouse.get_pos()
        if menu_buttons['lang_button'].body.collidepoint(
                (mx, my)) and click:  # switch language
            tools.change_language(languages=languages, 
                            menu_buttons=menu_buttons, 
                            simulations_content=simulations_content, 
                            text_dict=text_dict, user=user)
        click = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # LB
                    click = True
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    # menu_cycle, user.language, menu_buttons, simulations_content, text_dict
                    return True, user.language, menu_buttons, simulations_content, text_dict
            if event.type == pygame.QUIT:
                return False, user.language, menu_buttons, simulations_content, text_dict
        if isinstance(bkgr, list):
            user.screen.blit(bkgr[k // 5], backgrrect)
            k += 1
            if k == len(bkgr) * 5:
                k = 0
        else:  # if help window is launched from the simulation
            user.screen.blit(bkgr, backgrrect)
            user.screen.blit(transparent_surf, (0, 0))
        menu_buttons['lang_button'].draw(user=user)
        menu_buttons['lang_table'].draw(user=user)
        fps_val(False)
        pygame.display.update()
        clock.tick(user.fps)


def ingame_main_menu(
        languages=None,
        menu_buttons=None,
        text_dict=None,
        simulations_content=None,
        bkgr=None,
        user=None,
        sim_objects=None,
        COEFFICIENT=1.0):
    game_menu_cycle = True
    click = False
    k = 0.7
    switch = False
    saved_window = None
    saved_window_timer = None
    user.screen.fill('#000000')
    transparent_surf = pygame.Surface(user.size)
    transparent_surf.set_alpha(196)
    transparent_surf.fill('#000000')
    while game_menu_cycle:
        mx, my = pygame.mouse.get_pos()
        if menu_buttons['continue_button'].body.collidepoint(
                (mx, my)) and click:
            return True, languages, False  # simulation's cycle, languages, exit from the program
        elif menu_buttons['save_button'].body.collidepoint((mx, my)) and click:
            saved_window, saved_window_timer = simulation.save(
                sim_objects=sim_objects, 
                HOME_DIR=HOME_DIR,
                win_size=user.size,
                saved_w=saved_window, 
                saved_w_t=saved_window_timer)
        elif menu_buttons['ingame_settings_button'].body.collidepoint((mx, my)) and click:
            game_menu_cycle, user.language, menu_buttons, simulations_content, text_dict = settings_window(
                languages=languages, menu_buttons=menu_buttons, 
                simulations_content=simulations_content, 
                text_dict=text_dict, bkgr=bkgr, user=user,
                COEFFICIENT=COEFFICIENT)
        elif menu_buttons['ingame_help_button'].body.collidepoint((mx, my)) and click:
            game_menu_cycle = help_window(
                help_text=text_dict['help_text'], bkgr=bkgr, 
                user=user, COEFFICIENT=COEFFICIENT)
        # exit button
        elif menu_buttons['ingame_exit_button'].body.collidepoint((mx, my)) and click:
            # simulation's cycle, languages, exit from the program
            return False, languages, False
        click = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # LB
                    click = True
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    return True, languages, False
            if event.type == pygame.QUIT:
                return False, languages, True
        user.screen.blit(bkgr, (0, 0))
        user.screen.blit(transparent_surf, (0, 0))
        pygame.draw.rect(
            user.screen,
            (200 * k,
             200 * k,
             200 * k),
            (user.size[0] // 2 - 30 * COEFFICIENT,
             user.size[1] // 2 - 3 * user.size[1] / 31,
             20 * COEFFICIENT,
             2 * user.size[1] / 31))
        pygame.draw.rect(
            user.screen,
            (200 * k,
             200 * k,
             200 * k),
            (user.size[0] // 2 + 10 * COEFFICIENT,
             user.size[1] // 2 - 3 * user.size[1] / 31,
             20 * COEFFICIENT,
             2 * user.size[1] / 31))
        if k < 1 and not(switch):
            k += 0.01
        elif k > 0.7:
            k -= 0.01
            switch = True
        else:
            switch = False
        if saved_window_timer and int(
                round(time() * 1000)) - saved_window_timer < 3000:
            saved_window.draw(user=user)
        menu_buttons['continue_button'].draw(user=user)
        menu_buttons['save_button'].draw(user=user)
        menu_buttons['ingame_settings_button'].draw(user=user)
        menu_buttons['ingame_help_button'].draw(user=user)
        menu_buttons['ingame_exit_button'].draw(user=user)
        fps_val(False)
        pygame.display.update()
        clock.tick(user.fps)
    return False, languages, True  # simulation's cycle, languages, exit from the program


def mode_elements(
        selected_obj=None,
        velocity_graph_data=None,
        maximum=1.0,
        zoom=1.0,
        movement=[0, 0],
        user=None,
        COEFFICIENT=1.0):
    """This function draws all advanced mode graphic items."""
    pygame.draw.line(
        user.screen, '#555555',
        (30 * COEFFICIENT, user.size[1] -
         30 * COEFFICIENT),
        (30 * COEFFICIENT + 199,
         user.size[1] - 30 * COEFFICIENT), 1)  # scale line
    pygame.draw.line(
        user.screen,'#555555',
        (30 * COEFFICIENT, user.size[1] - 
         20 * COEFFICIENT),
        (30 * COEFFICIENT, user.size[1] - 
         40 * COEFFICIENT), 1)
    pygame.draw.line(
        user.screen, '#555555',
        (30 * COEFFICIENT + 99, user.size[1] -
         20 * COEFFICIENT),
        (30 * COEFFICIENT + 99, user.size[1] -
         40 * COEFFICIENT), 1)
    pygame.draw.line(
        user.screen, '#555555',
        (30 * COEFFICIENT + 199, user.size[1] -
         20 * COEFFICIENT),
        (30 * COEFFICIENT + 199, user.size[1] -
         40 * COEFFICIENT), 1)
    user.screen.blit(
        OBJ_INFO_FONT.render(
            "In 100px {} km.".format(
                round(10 ** 5 / zoom, 3)),
            True, '#555555'),
        (30 * COEFFICIENT,
         user.size[1] - 60 * COEFFICIENT))
    user.screen.blit(
        OBJ_INFO_FONT.render(
            '(0, 0)', True, '#444444'),
        (movement[0] * zoom + 6 * COEFFICIENT,
         movement[1] * zoom - 24 * COEFFICIENT))
    pygame.draw.circle(
        user.screen, '#444444',
        (movement[0] * zoom, 
        movement[1] * zoom), 4)
    if selected_obj is not None and len(velocity_graph_data) > 2:  # graph
        pygame.draw.aalines(user.screen, '#c80000', False, [
                            i[:2] for i in velocity_graph_data], 2)
        pygame.draw.line(
            user.screen, '#666666',
            (user.size[0] - 350 * COEFFICIENT, 
             user.size[1] - 35 * COEFFICIENT),
            (user.size[0] - 350 * COEFFICIENT, 
             user.size[1] - 235 * COEFFICIENT), 1)
        pygame.draw.line(
            user.screen, '#555555',
            (user.size[0] - 350 * COEFFICIENT,
             user.size[1] - 235 * COEFFICIENT),
            (user.size[0] - 355 * COEFFICIENT,
             user.size[1] - 235 * COEFFICIENT), 1)
        pygame.draw.line(
            user.screen, '#555555',
            (user.size[0] - 350 * COEFFICIENT,
             user.size[1] - 210 * COEFFICIENT),
            (user.size[0] - 355 * COEFFICIENT,
             user.size[1] - 210 * COEFFICIENT), 1)
        pygame.draw.line(
            user.screen, '#555555',
            (user.size[0] - 350 * COEFFICIENT,
             user.size[1] - 185 * COEFFICIENT),
            (user.size[0] - 355 * COEFFICIENT,
             user.size[1] - 185 * COEFFICIENT), 1)
        pygame.draw.line(
            user.screen, '#555555',
            (user.size[0] - 350 * COEFFICIENT,
             user.size[1] - 160 * COEFFICIENT),
            (user.size[0] - 355 * COEFFICIENT,
             user.size[1] - 160 * COEFFICIENT), 1)
        pygame.draw.line(
            user.screen, '#555555',
            (user.size[0] - 350 * COEFFICIENT,
             user.size[1] - 135 * COEFFICIENT),
            (user.size[0] - 355 * COEFFICIENT,
             user.size[1] - 135 * COEFFICIENT), 1)
        pygame.draw.line(
            user.screen, '#555555',
            (user.size[0] - 350 * COEFFICIENT,
             user.size[1] - 110 * COEFFICIENT),
            (user.size[0] - 355 * COEFFICIENT, 
            user.size[1] - 110 * COEFFICIENT), 1)
        pygame.draw.line(
            user.screen, '#555555',
            (user.size[0] - 350 * COEFFICIENT,
             user.size[1] - 85 * COEFFICIENT),
            (user.size[0] - 355 * COEFFICIENT,
             user.size[1] - 85 * COEFFICIENT), 1)
        pygame.draw.line(
            user.screen, '#555555',
            (user.size[0] - 350 * COEFFICIENT,
             user.size[1] - 60 * COEFFICIENT),
            (user.size[0] - 355 * COEFFICIENT,
             user.size[1] - 60 * COEFFICIENT), 1)
        pygame.draw.line(
            user.screen, '#555555',
            (user.size[0] - 355 * COEFFICIENT,
             user.size[1] - 35 * COEFFICIENT),
            (user.size[0] - 55 * COEFFICIENT,
             user.size[1] - 35 * COEFFICIENT), 1)
        pygame.draw.line(
            user.screen, '#555555',
            (user.size[0] - 55 * COEFFICIENT,
             user.size[1] - 35 * COEFFICIENT),
            (user.size[0] - 55 * COEFFICIENT,
             user.size[1] - 30 * COEFFICIENT), 1)
        velocity_graph_data_text = OBJ_INFO_FONT.render(
            str(round(maximum / 1000, 3)) + " km/s", True, '#c8c8c8')
        user.screen.blit(
            velocity_graph_data_text,
            (user.size[0] - 370 * COEFFICIENT -
             velocity_graph_data_text.get_width(),
             user.size[1] - 235 * COEFFICIENT -
             velocity_graph_data_text.get_height() // 2))
        velocity_graph_data_text = OBJ_INFO_FONT.render(
            "10 sec", True, '#c8c8c8')
        user.screen.blit(
            velocity_graph_data_text,
            (user.size[0] - 50 * COEFFICIENT -
             velocity_graph_data_text.get_width() // 2,
             user.size[1] - 20 * COEFFICIENT -
             velocity_graph_data_text.get_height() // 2))
# def calculate_camera_pos():


def simulation_loop(
        space_objects=None,
        simulation_name=None,
        images=None,
        menu_buttons=None,
        simulations_content=None,
        text_dict=None,
        languages=None,
        user=None,
        COEFFICIENT=1.0,
        DT=1.0,
        G=1.0,
        DIST_COEFF=1.0):
    zoom = 1.0
    movement_speed, movement = 4, [0, 0]
    movement_obj = [0, 0]  # pseudo-object needed for center zooming
    mx = my = None  # cursor coordinates
    selected_obj = None
    velocity_graph_data = []  # selected object's velocity dataset for graph
    maximum = 100  # maximum velocity value in a time interval
    velocity_add_timer = 0  # time interval for adding data to the graph
    moving_right = moving_left = moving_up = moving_down = shift_pressed = False
    sim_cycle = True
    pause = True # for fast loading, first pause is active
    initial_frames = 0 # after drawing 2nd frame engine starts work
    mode = False
    simulation_time = 0
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
                    screenshot_rect = pygame.Rect(
                        0, 0, user.size[0], user.size[1])
                    screenshot = display_surf.subsurface(
                        screenshot_rect)  # screenshot of display_surf
                    sim_cycle, languages, exit_from_prog = ingame_main_menu(
                        languages=languages, menu_buttons=menu_buttons, 
                        text_dict=text_dict, simulations_content=simulations_content,
                        bkgr=screenshot, user=user, sim_objects=space_objects, 
                        COEFFICIENT=COEFFICIENT)
                    if not(sim_cycle):
                        space_objects = []
                        if exit_from_prog:
                            return False, languages  # main_loop, languages
                        else:
                            return True, languages
                if event.key == K_e:
                    mode = not(mode)
                if event.key == K_LSHIFT:
                    shift_pressed = True
                if event.key == K_r:
                    user.screen.fill('#000000')
                    space_objects = []
                    space_objects = simulation.initialise(
                        name=simulation_name, 
                        images=images['objects'],
                        win_size=user.size,
                        display_surf=display_surf,
                        HOME_DIR=HOME_DIR)
                    [space_objects[i].update(zoom)
                     for i in range(len(space_objects))]
                if event.key == K_0:
                    movement = [0, 0]
                    movement_obj = [0, 0]
                    zoom = 1
                    [space_objects[i].update(zoom)
                     for i in range(len(space_objects))]
                if event.key == K_p:
                    pause = not(pause)
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # LBM
                    mx, my = pygame.mouse.get_pos()
                    if mode:
                        for o in range(len(space_objects)):
                            position_on_display = (
                                (space_objects[o].x *
                                 DIST_COEFF +
                                 movement[0]) * zoom,
                                (space_objects[o].y *
                                 DIST_COEFF +
                                 movement[1]) * zoom)
                            r_on_display = space_objects[o].r * \
                                zoom * DIST_COEFF
                            if - r_on_display < mx - position_on_display[0] < r_on_display and \
                                    - r_on_display < my - position_on_display[1] < r_on_display:
                                if selected_obj == o:
                                    movement_obj[0] = - space_objects[selected_obj].x * DIST_COEFF
                                    movement_obj[1] = - space_objects[selected_obj].y * DIST_COEFF
                                    selected_obj = None
                                    velocity_graph_data = []
                                else:
                                    selected_obj = o
                                break
                    elif not(shift_pressed):
                        img_name = list(images['objects'].keys())[
                            list(images['objects'].values()).index(
                                 images['objects']['star_img'])]  # search for a key by value
                        anObject = obj(int((mx / zoom - movement[0]) / DIST_COEFF), 
                                       int((my / zoom - movement[1]) / DIST_COEFF), 
                                       images['objects']['star_img'], img_name, 
                                       16e+6, 1e+22)
                        anObject.update(zoom)
                        space_objects.append(anObject)
                if event.button == 4:  # mouse wheel forward
                    zoom += 0.005 + 0.05 * zoom
                    zoom = round(zoom, 3)
                    [space_objects[i].update(zoom)
                     for i in range(len(space_objects))]
                elif event.button == 5:  # backward
                    if zoom > 0.005:
                        zoom -= (0.005 + 0.05 * zoom)
                        zoom = round(zoom, 3)
                        [space_objects[i].update(zoom)
                         for i in range(len(space_objects))]
                        if zoom < 0.005:
                            zoom = 0.005
            if event.type == MOUSEBUTTONUP:
                if event.button == 1 and mx and shift_pressed and not(mode):
                    img_name = list(
                        images['objects'].keys())[
                        list(
                            images['objects'].values()).index(
                            images['objects']['star_img'])]  # search for a key by value
                    anObject = obj(int((mx / zoom - movement[0]) / DIST_COEFF),
                                   int((my / zoom - movement[1]) / DIST_COEFF),
                                   images['objects']['star_img'], img_name,
                                   16e+6, 1e+22,
                                   (pygame.mouse.get_pos()[0] - mx) * 10,
                                   (pygame.mouse.get_pos()[1] - my) * 10)
                    anObject.update(zoom=zoom)
                    space_objects.append(anObject)
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
                return False, languages
        if moving_up:
            movement_obj[1] -= movement_speed / zoom
        if moving_down:
            movement_obj[1] += movement_speed / zoom
        if moving_left:
            movement_obj[0] -= movement_speed / zoom
        if moving_right:
            movement_obj[0] += movement_speed / zoom
        if initial_frames < 2:
            initial_frames += 1
        elif initial_frames == 2: 
            pause = False
            initial_frames = 3
        if not(pause):
            engine.step(space_objects=space_objects, DT=DT, G=G)
            simulation_time += DT
        if selected_obj is not None and not(pause):  
            # camera follows the selected object
            movement[0] = - space_objects[selected_obj].x * \
                DIST_COEFF + (user.size[0] // 2) / zoom
            movement[1] = - space_objects[selected_obj].y * \
                DIST_COEFF + (user.size[1] // 2) / zoom
            if len(velocity_graph_data) >= 200:
                velocity_graph_data.pop(0)
                for t in range(len(velocity_graph_data)):
                    velocity_graph_data[t][0] -= 1.5 * COEFFICIENT
            if int(round(time() * 1000)) - \
                    velocity_add_timer > 50 or velocity_add_timer == 0:  # addition velocity data
                velocity_add_timer = int(round(time() * 1000))
                obj_velocity = hypot(
                    space_objects[selected_obj].vx,
                    space_objects[selected_obj].vy)
                velocity_graph_data.append(
                    [(user.size[0] - 350 + len(velocity_graph_data) * 1.5) * COEFFICIENT,
                     (user.size[1] - 35 - 200 * obj_velocity / maximum) * COEFFICIENT,
                     obj_velocity])  # [X on display, Y on display, velocity]
                if max(velocity_graph_data, key=lambda x: x[2])[2] > 0 and \
                        max(velocity_graph_data, key=lambda x: x[2])[2] != maximum:
                    maximum = max(velocity_graph_data, key=lambda x: x[2])[2]
                    for t in range(len(velocity_graph_data)):  
                        # changing y-coordinate for all data
                        velocity_graph_data[t][1] = (user.size[1] - 35 - 
                            200 * velocity_graph_data[t][2] / maximum) * COEFFICIENT
        else:  # camera follows the movement_obj
            movement[0] = - movement_obj[0] + (user.size[0] // 2) / zoom
            movement[1] = - movement_obj[1] + (user.size[1] // 2) / zoom
        display_surf.fill('#000000')
        [space_objects[i].draw(zoom=zoom, movement=movement, mode=mode, 
         COEFFICIENT=COEFFICIENT, DIST_COEFF=DIST_COEFF)
         for i in range(len(space_objects))]  # drawing all objects
        user.screen.blit(display_surf, (0, 0))
        if mode:
            mode_elements(
                selected_obj=selected_obj,
                velocity_graph_data=velocity_graph_data,
                maximum=maximum, zoom=zoom,
                movement=movement, user=user,
                COEFFICIENT=COEFFICIENT)
        if len(space_objects) > 0:
            fps_val(game=True, zoom=zoom,
                    movement=movement, 
                    space_object=space_objects[-1],
                    obj_amount=len(space_objects),
                    simulation_time=simulation_time,
                    DIST_COEFF=DIST_COEFF)
        else:
            fps_val(game=True, zoom=zoom,
                    movement=movement,
                    simulation_time=simulation_time,
                    DIST_COEFF=DIST_COEFF)
        pygame.display.update()
        clock.tick(user.fps)
