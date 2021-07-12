import pygame
from inspect import currentframe, getframeinfo
from os.path import dirname, abspath
from time import time
from ui.settings import settings


user = settings(autosize=True)
display_surf = pygame.Surface(pygame.display.get_window_size())
display_surf.set_alpha(None)
clock = pygame.time.Clock()
cur_time = int(round(time() * 1000))
frames = 0  # frames' counter
fps = 0
if pygame.display.get_window_size()[0] / 1920 < pygame.display.get_window_size()[1] / 1080:  
    COEFFICIENT = pygame.display.get_window_size()[0] / 1920
else:
    COEFFICIENT = pygame.display.get_window_size()[1] / 1080
DIST_COEFF = 1e-6  # distance coefficient transformates meters to megameters
G = 6.67430e-11  # real value = 6.67430e-11. Use decimal to calculate that accurately
SPEED = 60 * 60 * 24  # simulation speed in seconds
DT = (1.0 / user.fps) * SPEED  # time step for objects
filename = getframeinfo(currentframe()).filename  # project's directory
HOME_DIR = dirname(
    abspath(filename)).replace(
    "\\", "/") + "/"
DEAFULT_FONT = pygame.font.Font(
    HOME_DIR + 'data/Anonymous Pro B.ttf',
    round(24 *COEFFICIENT))
OBJ_INFO_FONT = pygame.font.Font(
    HOME_DIR +'data/Anonymous Pro B.ttf',
    round(16 * COEFFICIENT))
HELP_FONT = pygame.font.Font(
    HOME_DIR + 'data/Anonymous Pro B.ttf',
    round(30 * COEFFICIENT))
font_size = 1  # informational font size
SIM_INFO_FONT = pygame.font.Font(
    HOME_DIR + 'data/Anonymous Pro B.ttf', font_size)
while (560 * COEFFICIENT) / SIM_INFO_FONT.render(
        "X", True, '#c8c8c8').get_width() >= 43:  # calculating necessary font size
    font_size += 1
    SIM_INFO_FONT = pygame.font.Font(
        HOME_DIR + 'data/Anonymous Pro B.ttf', font_size)
