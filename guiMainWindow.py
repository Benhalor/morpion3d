from __future__ import division

import pygame
from guiGameWindow2D import GameWindow2D
from guiGameWindow3D import GameWindow3D

import time
from threading import Thread
import threading
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
        self.__lockEvent = threading.Lock()

        self.__boolMoveLeft = False
        self.__boolMoveRight = False
        self.__boolMoveUp = False
        self.__boolMoveDown = False
        self.__boolRightClick = False

    def run(self):
        self.__lockEvent.acquire()
        pygame.init()
        self._screen = pygame.display.set_mode((640, 480))
        if self.dim3Dor2D == 2:
            self._gui = GameWindow2D(self, 300, [100, 100], self.dim)
        elif self.dim3Dor2D == 3:
            self._gui = GameWindow3D(self, 10, self._gridSize)

        self.textMessage = "New window started."

        self.update_screen()

        # Release lock at starting
        try:
            self.__lockEvent.release()
        except:
            pass

        # Event management
        starting = time.time()
        move = False

        while self._boolContinue:

            # Rotate view
            move = self.__boolMoveLeft or self.__boolMoveRight or self.__boolMoveUp or self.__boolMoveDown \
                   or self.__boolRightClick
            if move:
                if time.time() - starting >= 0.06:
                    if self.__boolMoveLeft:
                        self._gui.move("left", 0.1)
                    elif self.__boolMoveRight:
                        self._gui.move("right", 0.1)
                    elif self.__boolMoveUp:
                        self._gui.move("up", 0.1)
                    elif self.__boolMoveDown:
                        self._gui.move("down", 0.1)
                    elif self.__boolRightClick:
                        x = pygame.mouse.get_pos()[0]
                        if x < 200:
                            self._gui.move("left", 0.001 * (200 - x))
                        elif x > 400:
                            self._gui.move("right", 0.001 * (x - 400))
                    starting = time.time()
                    event = pygame.event.poll()
            else:
                event = pygame.event.wait()

            # rotate
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    self.__boolMoveLeft = True
                elif event.key == K_RIGHT:
                    self.__boolMoveRight = True
                elif event.key == K_UP:
                    self.__boolMoveUp = True
                elif event.key == K_DOWN:
                    self.__boolMoveDown = True
            if event.type == KEYUP:
                if event.key == K_LEFT:
                    self.__boolMoveLeft = False
                elif event.key == K_RIGHT:
                    self.__boolMoveRight = False
                elif event.key == K_UP:
                    self.__boolMoveUp = False
                elif event.key == K_DOWN:
                    self.__boolMoveDown = False

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1 and self._wantToPlay:  # If left click, select cell if it is your turn
                    cell = self._gui.playedCell
                    if cell != [-1, -1]:
                        self.update_screen()
                        self._cell = cell
                        self.__lockEvent.release()
                elif event.button == 3 :
                    self.__boolRightClick = True
            if event.type == MOUSEBUTTONUP:
                if event.button == 3:  # If right click
                    self.__boolRightClick = False
            if event.type == MOUSEMOTION :
                #self.gui.move("left")
                self._gui.detect_cell_pos(event.pos)
                self.update_screen()
            if event.type == QUIT:
                self.stop()


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
        # If pygame is not yet started, wait to start
        self.__lockEvent.acquire()
        self.__lockEvent.release()

        self._wantToPlay = True
        self._cell = None
        self.__lockEvent.acquire()

        # Wait the run loop to release the lock (only when cell is clicked)
        self.__lockEvent.acquire()
        self.__lockEvent.release()
        self._wantToPlay = False
        return self._cell

    def send_state_matrix(self, matrix):
        self._gui.stateMatrix = matrix

    def stop(self):
        self._boolContinue = False
        try:
            pygame.event.post(pygame.event.Event(QUIT))
        except:
            pass
        try:
            self.__lockEvent.release()
        except:
            pass
