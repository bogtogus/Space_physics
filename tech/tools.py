def split_by_separator(string, length, separator=' '):
    """This function splits received text by 
    a given string length and a separator."""
    upper_border = 0
    output = []
    while len(string) > 0:
        if len(string) <= length:
            output.append(string.strip())
            break
        try:
            upper_border = string.rindex(separator, 0, length + 1)
        except ValueError:
            output.append(string[:length].strip())
            string = string[length:len(string)]
            continue
        output.append(string[:upper_border].strip())
        string = string[upper_border + 1:len(string)]
    return output


def change_language(languages=None, menu_buttons=None, 
                    simulations_content=None, text_dict=None, user=None):
    """This function changes the language from the list to the next one."""
    from sqlite3 import connect
    from constants import HOME_DIR
    db = connect(HOME_DIR + 'database.db')
    sql = db.cursor()
    for i in range(len(languages)):
        if languages[i] == user.language:
            if i == len(languages) - 1:
                user.language = languages[0]
            else:
                user.language = languages[i + 1]
            break
    for i in sql.execute(
        "SELECT class, name, text FROM {}".format(
            user.language)):  # buttons
        if i[0] == 'button':
            menu_buttons[i[1]].text = i[2]
            menu_buttons[i[1]].update()
        elif i[0] in ('info', 'text'):
            text = split_by_separator(i[2], 43)
            try:
                if i[0] == "info":
                    simulations_content[i[1]][3] = text
                elif i[0] == "text":
                    text_dict[i[1]] = text
            except Exception as e:
                continue
    db.close()


def db_change_language(user=None, languages=None):
    from sqlite3 import connect
    from constants import HOME_DIR
    if user.language in languages:
        db = connect(HOME_DIR + 'database.db')
        sql = db.cursor()
        sql.execute(
            "UPDATE settings SET language = '{}' WHERE user = 'user01'".format(
                user.language))
        db.commit()
        db.close()
