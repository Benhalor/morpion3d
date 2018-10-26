from __future__ import division

import pygame
from guiGameWindow2D import GameWindow2D
from guiGameWindow3D import GameWindow3D

import time
from threading import Thread
from pygame.locals import *


class MainWindow(Thread):

    def __init__(self, dim3Dor2D, gridSize):
        Thread.__init__(self)
        self.dim3Dor2D = dim3Dor2D
        self._gridSize = gridSize
        self._boolContinue = True
        self._wantToPlay = False
        self._cell = None
        self._screen = None
        self._gui = None

    def run(self):
        pygame.init()
        self._screen = pygame.display.set_mode((640, 480))
        if self.dim3Dor2D == 2:
            self._gui = GameWindow2D(self, 300, [100, 100], self.dim)
        elif self.dim3Dor2D == 3:
            self._gui = GameWindow3D(self, 10, self._gridSize)

        self.textMessage = "New window started."

        self.update_screen()


        # Event management
        starting = time.time()
        move = False
        while self._boolContinue:
            if time.time() - starting >= 0.04 and move :
                if pygame.mouse.get_pos()[0] < 200:
                    self._gui.move("left", 0.0004 * (200 - pygame.mouse.get_pos()[0]))
                elif pygame.mouse.get_pos()[0] > 400:
                    self._gui.move("right", 0.0004 * (pygame.mouse.get_pos()[0] - 400))
                starting = time.time()
            for event in pygame.event.get():
                if self._wantToPlay:
                    if event.type == KEYDOWN:
                        if event.key == K_LEFT:
                            self._gui.move("left",0.1)
                        elif event.key == K_RIGHT:
                            self._gui.move("right",0.1)
                        elif event.key == K_UP:
                            self._gui.move("up",0.1)
                        elif event.key == K_DOWN:
                            self._gui.move("down",0.1)
                    if event.type == MOUSEBUTTONDOWN:
                        if event.button == 1:  # If left click
                            cell = self._gui.playedCell
                            if cell != [-1, -1]:
                                self.update_screen()
                                self._cell = cell
                        elif event.button == 3 :
                            move = True
                    if event.type == MOUSEBUTTONUP:
                        if event.button == 3:  # If right click
                            move = False
                    if event.type == MOUSEMOTION :
                        #self.gui.move("left")
                        self._gui.detect_cell_pos(event.pos)
                        self.update_screen()
                if event.type == QUIT:
                    self._boolContinue = False

        pygame.quit()
        print("End of thread guiMainWIndows")


    def update_screen(self):
        self._gui.update_screen()
        font = pygame.font.Font(None, 24)
        text = font.render(self.textMessage, 1, (255, 255, 255))
        self.screen.blit(text, (10, 450))
        pygame.display.flip()

    def _get_screen(self):
        return self._screen
    screen = property(_get_screen)

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
        self._gui.stateMatrix = matrix

    def stop(self):
        self._boolContinue = False

