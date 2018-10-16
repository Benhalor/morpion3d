from __future__ import division

import pygame
import sys
from guiGameWindow2D import GameWindow2D
from guiGameWindow3D import GameWindow3D

from threading import Thread
from pygame.locals import *

class MainWindow(Thread):

    def __init__(self,dim3Dor2D,dim):
        Thread.__init__(self)
        self.dim3Dor2D = dim3Dor2D
        self.dim = dim

        self.screen = pygame.display.set_mode((640, 480))
        if self.dim3Dor2D == 2:
            self.gui = GameWindow2D(self, 300, [100, 100], self.dim)
        elif self.dim3Dor2D == 3:
            self.gui = GameWindow3D(self, 300, [300, 10], self.dim)

        self.textMessage = "Bonjour le monde. Ceci est un test."

    def run(self):

        # The following part should not be in the init. Otherwise, the event handler is in the wrong thread
        pygame.init()
        self.update_screen()

        boolContinue = True
        # Event management
        while boolContinue:
            for event in pygame.event.get():
                pygame.event.wait()
                if event.type == QUIT:
                    boolContinue = False
                    print("quit")
                    pygame.quit()
        print("End of thread guiMainWIndows")


    def update_screen(self):
        self.gui.update_screen()
        font = pygame.font.Font(None, 24)
        text = font.render(self.textMessage, 1, (255, 255, 255))
        self.screen.blit(text, (10, 450))
        pygame.display.flip()

    def set_message(self, newText):
        self.textMessage = newText
        self.update_screen()

    def get_screen(self):
        return self.screen

    def get_played_cell(self):
        boolContinue = True
        while boolContinue:
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:  # If left click
                        cell = self.gui.get_played_cell()
                        if cell != [-1, -1]:
                            self.update_screen()
                            return cell
                if event.type == MOUSEMOTION:
                    self.gui.detect_cell_pos(event.pos)
                    self.update_screen()
                if event.type == QUIT:
                    boolContinue = False
                    print("quit")
                    pygame.quit()

    def send_state_matrix(self, matrix):
        self.gui._set_state_matrix(matrix)