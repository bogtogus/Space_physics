from time import strftime, strptime, ctime, time
from sqlite3 import connect
from global_values import HOME_DIR, COEFFICIENT, DEAFULT_FONT
from tech.button import button
import pygame 


def initialise(
        name=None,
        images={},
        win_size=None,
        display_surf=None,
        HOME_DIR=None):
    """This function creates a list of simulanion's objects."""
    import traceback
    from .object import obj


    try:
        obj_list = []
        db = connect(HOME_DIR + 'simulations.db')
        sql = db.cursor()
        simulation = list(sql.execute(
            "SELECT x, y, Image_name, Radius, Mass, Vx, Vy, id FROM s_{}".format(name)))
        for ob in simulation:
            try:
                img = images[ob[2]]
                img_name = ob[2]
            except Exception:
                img = img_name = 'circle'
            anObject = obj(float(ob[0]), float(ob[1]), 
                           img, img_name, 
                           float(ob[3]), float(ob[4]), win_size=win_size, display_surf=display_surf)
            if float(ob[5]) != 0 or float(ob[6]) != 0:  # vx, vy
                anObject.vx = float(ob[5])
                anObject.vy = float(ob[6])
            obj_list.append(anObject)
        db.close()
        if len(obj_list) == 0:
            obj_list = ['error', 'List is empty.']
    except Exception:
        with open(HOME_DIR + 'log.txt', 'a') as log:
            log.write('\n{} [{}]\n'.format(
                traceback.format_exc(), strftime(
                    '%x %X',
                    strptime(ctime()))))
        obj_list = ['error', 'An error has occurred. Check log.txt.']
    return obj_list


def save(
        sim_objects=None, 
        HOME_DIR=None,
        win_size=None,
        saved_w=None, 
        saved_w_t=None):
    name_of_saved = 's_' + str(strftime(
        '%x %X', 
        strptime(ctime()))).replace('/', '_').replace(':', '_').replace(" ", "_")
    db = connect(HOME_DIR + 'simulations.db')
    sql = db.cursor()
    command = """CREATE TABLE IF NOT EXISTS {} 
        (id INTEGER PRIMARY KEY,
         x TEXT,
         y TEXT,
         Image_name TEXT,
         Radius TEXT CHECK (Radius >= 0),
         Mass TEXT CHECK (Mass >= 0),
         Vx TEXT,
         Vy TEXT
    );""".format(name_of_saved)
    sql.execute(command)
    i = 0
    for obj in sim_objects:
        parameters = (
            i, obj.x, obj.y, 
            obj.img_name, obj.r,
            obj.m, obj.vx, obj.vy)
        sql.execute(
            "INSERT INTO {} VALUES (?, ?, ?, ?, ?, ?, ?, ?);".format(name_of_saved), 
            parameters)
        i += 1
    db.commit()
    db.close()
    saved_text = DEAFULT_FONT.render("Saved", True, '#ee1111')
    saved_w = button(
        place=[35 * COEFFICIENT,
               win_size[1] - 75 * COEFFICIENT],
        size=(saved_text.get_width() + 70 * COEFFICIENT,
              50 * COEFFICIENT),
        color='#009900',
        button_text="Saved.",
        font_size=round(24 * COEFFICIENT),
        font_color='#dddddd',
        surface=pygame.display.get_surface(),
        HOME_DIR=HOME_DIR)
    saved_w_t = int(round(time() * 1000))
    return saved_w, saved_w_t
