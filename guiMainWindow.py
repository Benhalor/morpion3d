from __future__ import division

import pygame
from guiGameWindow2D import GameWindow2D


class MainWindow:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480))
        self.gui2D = GameWindow2D(self.screen, 300, [100, 100])


gui = MainWindow()
