from __future__ import division

import pygame
from guiGameWindow2D import GameWindow2D


class MainWindow:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480))
        self.gui2D = GameWindow2D(self, 300, [100, 100])

        self.textMessage = "Bonjour le monde. Ceci est un test."

        self.gui2D.start()
        self.update_screen()

    def update_screen(self):
        self.gui2D.update_screen()
        font = pygame.font.Font(None, 24)
        text = font.render(self.textMessage, 1, (255, 255, 255))
        self.screen.blit(text, (450, 10))
        pygame.display.flip()

    def set_message(self,newText):
        self.textMessage = newText
        self.update_screen()

    def get_screen(self):
        return self.screen

    def get_played_cell(self):
        return self.gui2D.get_played_cell()

    def send_state_matrix(self, matrix):
        self.gui2D._set_state_matrix(matrix)

gui = MainWindow()
