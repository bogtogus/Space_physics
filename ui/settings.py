class settings:
    def __init__(self, fps=50, size=(1920, 1080), autosize=False):
        import pygame
        pygame.init()
        pygame.display.set_caption('Space_physics')
        self.fps = fps
        if autosize:
            size = (
                pygame.display.Info().current_w,
                pygame.display.Info().current_h)
        self.size = size
        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        self.language = None
