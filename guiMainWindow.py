from __future__ import division

import pygame
from guiGameWindow2D import GameWindow2D
from guiGameWindow3DPerspectiveProjection import GameWindow3D

from threading import Thread
from pygame.locals import *


class MainWindow(Thread):

    def __init__(self, dim3Dor2D, dim):
        Thread.__init__(self)
        self.dim3Dor2D = dim3Dor2D
        self.dim = dim
        self._boolContinue = True
        self._wantToPlay = False
        self._cell = None

    def run(self):

        # The following part should not be in the init. Otherwise, the event handler is in the wrong thread
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480))
        if self.dim3Dor2D == 2:
            self.gui = GameWindow2D(self, 300, [100, 100], self.dim)
        elif self.dim3Dor2D == 3:
            self.gui = GameWindow3D(self, 10, [300, 10], self.dim)

        self.textMessage = "Bonjour le monde. Ceci est un test."

        self.update_screen()


        # Event management
        while self._boolContinue:
            for event in pygame.event.get():
                if self._wantToPlay:
                    if event.type == KEYDOWN:
                        if event.key == K_LEFT:
                            self.gui.move("left")
                        elif event.key == K_RIGHT:
                            self.gui.move("right")
                        elif event.key == K_UP:
                            self.gui.move("up")
                        elif event.key == K_DOWN:
                            self.gui.move("down")
                    if event.type == MOUSEBUTTONDOWN:
                        if event.button == 1:  # If left click
                            cell = self.gui.get_played_cell()
                            if cell != [-1, -1]:
                                self.update_screen()
                                self._cell = cell
                    if event.type == MOUSEMOTION:
                        #self.gui.move("left")
                        self.gui.detect_cell_pos(event.pos)
                        self.update_screen()
                if event.type == QUIT:
                    self._boolContinue = False

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
        while not self.isAlive() and self._boolContinue:
            pass

        self._wantToPlay = True
        self._cell = None

        while self._cell is None and self._boolContinue:
            pass
        self._wantToPlay = False
        return self._cell

    def send_state_matrix(self, matrix):
        self.gui._set_state_matrix(matrix)

    def stop(self):
        self._boolContinue = False

