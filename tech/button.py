import pygame


class button():
    def __init__(
            self,
            place=[0, 0],
            size=(0, 0),
            color='#c8c8c8',
            button_text='',
            font_size=16,
            font_color='#000000',
            path='data/Anonymous Pro B.ttf',
            surface=None,
            HOME_DIR=None):
        self.place = place
        self.size = size
        self.body = pygame.Rect(
            self.place[0],
            self.place[1],
            self.size[0],
            self.size[1])
        self.color = color
        self.select = False
        self.select_color = '#005ffe'
        self.text = button_text
        self.font = pygame.font.Font(HOME_DIR + path, font_size)
        self.font_color = font_color
        self.font_size = font_size
        self.surface = surface
        self.print_text = self.font.render(self.text, True, self.font_color)
        text_x = self.place[0] + \
            (self.size[0] - self.print_text.get_width()) // 2
        text_y = self.place[1] + \
            (self.size[1] - self.print_text.get_height()) // 2
        self.text_pos = [text_x, text_y]

    def update(self) -> None:
        self.print_text = self.font.render(self.text, True, self.font_color)
        self.body = pygame.Rect(
            self.place[0],
            self.place[1],
            self.size[0],
            self.size[1])
        text_x = self.place[0] + \
            (self.size[0] - self.print_text.get_width()) // 2
        text_y = self.place[1] + \
            (self.size[1] - self.print_text.get_height()) // 2
        self.text_pos = [text_x, text_y]

    def draw(self, user=None) -> None:
        if not(self.select):
            pygame.draw.rect(user.screen, self.color, self.body)
        else:
            pygame.draw.rect(user.screen, self.select_color, self.body)
            pygame.draw.rect(user.screen, '#c8c8c8', self.body, 1)
        user.screen.blit(self.print_text, self.text_pos)

    def copy(self):
        """Creates a new button with the same data."""
        copied_button = button()
        for key, value in self.__dict__.items():
            copied_button.__dict__[key] = value.copy() if type(value) in [
                list, dict, set] else value
        return copied_button
