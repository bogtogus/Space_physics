def init_content():
    """This function creates all main dicts, lists and gets current language."""
    from global_values import COEFFICIENT, HOME_DIR, user
    from tech.button import button
    from tech.tools import split_by_separator
    from sqlite3 import connect
    import pygame
    from os import listdir

    height = 2 * user.size[1] / 31  # button's parameter
    width = round(400 * COEFFICIENT)  # button's parameter
    languages = []
    db = connect(HOME_DIR + 'simulations.db')
    sql = db.cursor()
    simulations_list = map(lambda x: x[0][2:], sorted(list(
        sql.execute(
            "SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%'"))))
    db.close()
    db = connect(HOME_DIR + 'database.db')
    sql = db.cursor()
    for i in sql.execute(
            "SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%'"):  # languages
        if i[0] != 'settings' and len(i[0]) == 2:
            languages.append(i[0])
    user.language = sql.execute(
        "SELECT language FROM settings WHERE user ='user01'").fetchone()[0]
    menu_buttons = {}
    for i in sql.execute(
            "SELECT class, name, text, color, font_color FROM {}".format(
            user.language)):  # buttons
        if i[0] == 'button':
            init_button = button(
                size=(width, height),
                color=i[3],
                button_text=i[2],
                font_size=round(30 * COEFFICIENT),
                font_color=i[4],
                HOME_DIR=HOME_DIR)
            menu_buttons.update({i[1]: init_button})
    menu_buttons['choose_button'].place = [
        user.size[0] // 2 - width // 2, user.size[1] // 2]
    menu_buttons['settings_button'].place = [
        user.size[0] // 2 - width // 2, user.size[1] // 2 + height * 1.5]
    menu_buttons['help_button'].place = [
        user.size[0] // 2 - width // 2, user.size[1] // 2 + height * 3]
    menu_buttons['exit_button'].place = [
        user.size[0] // 2 - width // 2, user.size[1] // 2 + height * 4.5]
    menu_buttons['lang_button'].size = (round(200 * COEFFICIENT), height)
    menu_buttons['lang_table'].size = (round(200 * COEFFICIENT), height)
    menu_buttons['lang_button'].place = [
        user.size[0] // 2 - menu_buttons['lang_button'].size[0] // 2, 
        user.size[1] // 2]
    menu_buttons['lang_table'].place = [
        user.size[0] // 2 - 3.25 * menu_buttons['lang_button'].size[0] // 2, 
        user.size[1] // 2]
    menu_buttons['ingame_settings_button'].place = [
        user.size[0] // 2 - width // 2, user.size[1] // 2 + height * 3]
    menu_buttons['ingame_help_button'].place = [
        user.size[0] // 2 - width // 2, user.size[1] // 2 + height * 4.5]
    menu_buttons['ingame_exit_button'].place = [
        user.size[0] // 2 - width // 2, user.size[1] // 2 + height * 6]
    menu_buttons['continue_button'].place = [
        user.size[0] // 2 - width // 2, user.size[1] // 2]
    menu_buttons['save_button'].place = [
        user.size[0] // 2 - width // 2, user.size[1] // 2 + height * 1.5]
    for b in menu_buttons.keys():
        menu_buttons[b].update()
    help_text = sql.execute(
        "SELECT text FROM '{}' WHERE class = 'text' and name = 'help_text'".format(
            user.language)).fetchone()[0]
    help_text = split_by_separator(help_text, 43)
    text_dict = {}
    text_dict.update({'help_text': help_text})
    menu_buttons['start_button'].size = (round(560 * COEFFICIENT), height)
    menu_buttons['start_button'].place = [
        user.size[0] // 2 +
        width // 2 +
        height // 2,
        user.size[1] -
        height * 1.5]
    menu_buttons['start_button'].update()
    images = {"objects": {}, "background": [], "logo": None}
    for i in range(1, 16):  # animated background
        images['background'].append(
            pygame.transform.scale(
                pygame.image.load(
                    HOME_DIR + 'data/backgr/backgr2_' +
                    str(i) + '.png'),
                (user.size[0], user.size[1])))
    for item in listdir(HOME_DIR + 'data'):  # logotype and objects' images
        if item == 'logo.png':
            logo = pygame.image.load(HOME_DIR + 'data/logo.png')
            logo = pygame.transform.scale(logo,
                                          (int(logo.get_width() * COEFFICIENT),
                                           int(logo.get_height() * COEFFICIENT)))
            images['logo'] = logo
        elif len(item.split('.')) == 2 and item.split('.')[1] in ('png', 'jpg'):
            images['objects'].update({str(item.split('.')[0] + '_img'): 
                pygame.image.load(HOME_DIR + 'data/' + item).convert_alpha()})
    counter = 0
    simulations_content = {}
    for sim in simulations_list:  # simulations's content
        try:
            image = pygame.transform.scale(
                pygame.image.load(
                    HOME_DIR + 'data/simulations/' +
                    sim + '/preview.png').convert(),
                (round(540 * COEFFICIENT),
                 round(540 * COEFFICIENT)))
        except Exception:
            image = pygame.transform.scale(
                pygame.image.load(
                    HOME_DIR +
                    'data/simulations/noimage.png').convert(),
                (round(540 * COEFFICIENT),
                 round(540 * COEFFICIENT)))
        try:
            text = sql.execute(
                "SELECT text FROM '{}' WHERE class = 'info' and name = '{}'".format(
                    user.language, sim)).fetchone()[0]
            text = text.replace('\n', ' ')
        except Exception as e:
            text = "Text doesn't exist."
        text = split_by_separator(text, 43)
        sim_button = button(
            size=(width, height),
            color='#545454',
            button_text=sim,
            font_size=round(30 * COEFFICIENT),
            font_color='#dddddd',
            HOME_DIR=HOME_DIR)
        sim_button.place = [
            user.size[0] // 2 -
            sim_button.size[0] // 2,
            sim_button.size[1] / 2 +
            sim_button.size[1] * 1.5 *
            counter]
        sim_button.update()
        simulations_content.update({sim: [sim, sim_button, image, text]})
        counter += 1
    db.close()
    return simulations_content, menu_buttons, images, languages, text_dict
