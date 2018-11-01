from __future__ import division

import pygame
from guiGameWindow3D import GameWindow3D

import time
import threading
from pygame.locals import *


class MainWindow(threading.Thread):

    def __init__(self, gridSize):
        threading.Thread.__init__(self)
        self.__gridSize = gridSize
        self.__boolContinue = True
        self.__wantToPlay = False
        self.__cell = None
        self.__screen = None
        self.__gui = None
        self.__lockEvent = threading.Lock()

        self.__textMessage = " "

        self.__boolMoveLeft = False
        self.__boolMoveRight = False
        self.__boolMoveUp = False
        self.__boolMoveDown = False
        self.__boolRightClick = False

    def run(self):
        self.__lockEvent.acquire()
        pygame.init()
        self.__screen = pygame.display.set_mode((640, 480))
        self.__gui = GameWindow3D(self, 10, self.__gridSize)

        self.__textMessage = "New window started."

        self.update_screen()

        # Release lock at starting
        try:
            self.__lockEvent.release()
        except:
            pass

        # Event management
        starting = time.time()
        pygame.event.clear()

        while self.__boolContinue:

            # Rotate view
            move = self.__boolMoveLeft or self.__boolMoveRight or self.__boolMoveUp or self.__boolMoveDown \
                   or self.__boolRightClick
            if move:
                if time.time() - starting >= 0.03:
                    if self.__boolMoveLeft:
                        self.__gui.move("left", 0.07)
                    if self.__boolMoveRight:
                        self.__gui.move("right", 0.07)
                    if self.__boolMoveUp:
                        self.__gui.move("up", 0.07)
                    if self.__boolMoveDown:
                        self.__gui.move("down", 0.07)
                    if self.__boolRightClick:
                        x = pygame.mouse.get_pos()[0]
                        if x < 200:
                            self.__gui.move("left", 0.001 * (200 - x))
                        elif x > 400:
                            self.__gui.move("right", 0.001 * (x - 400))
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
                if event.button == 1 and self.__wantToPlay:  # If left click, select cell if it is your turn
                    cell = self.__gui.playedCell
                    if cell != [-1, -1]:
                        self.update_screen()
                        self.__cell = cell
                        self.__lockEvent.release()
                elif event.button == 3:
                    self.__boolRightClick = True
            if event.type == MOUSEBUTTONUP:
                if event.button == 3:  # If right click
                    self.__boolRightClick = False
            if event.type == MOUSEMOTION:
                self.__gui.detect_cell_pos(event.pos)
                self.update_screen()
            if event.type == QUIT:
                print("Gui Event quit")
                print(event)
                self.stop()

        pygame.quit()
        print("End of thread guiMainWIndows")

    def update_screen(self):
        self.__gui.update_screen()
        font = pygame.font.Font(None, 24)
        text = font.render(self.__textMessage, 1, (255, 255, 255))
        self.screen.blit(text, (10, 450))
        pygame.display.flip()

    def __get_screen(self):
        return self.__screen

    screen = property(__get_screen)

    def __get_message(self):
        return self.__textMessage

    def __set_message(self, newText):
        self.__textMessage = newText
        self.update_screen()

    textMessage = property(__get_message,__set_message)

    def get_played_cell(self):
        # If pygame is not yet started, wait to start
        self.__lockEvent.acquire()
        self.__lockEvent.release()

        self.__wantToPlay = True
        self.__cell = None
        self.__lockEvent.acquire()

        # Wait the run loop to release the lock (only when cell is clicked)
        self.__lockEvent.acquire()
        self.__lockEvent.release()
        self.__wantToPlay = False
        return self.__cell

    def highlight_winning_cell(self,cell):
        """Change the color of the winning cells"""
        if type(cell) != tuple:
            raise TypeError("Argument 'cell': expected 'tuple', got " + str(type(cell)))
        if len(cell) != 3:
            raise ValueError("Tuple 'cell' should have 3 elements, but has " + str(len(cell)))
        if type(cell[0]) != int or type(cell[1]) != int or type(cell[2]) != int:
            raise TypeError("Argument 'cell' should be a tuple of integers")
        self.__gui.highlight_winning_cell(cell)

    def highlight_played_cell(self,cell):
        """Change the color of the played cell"""
        if type(cell) != tuple:
            raise TypeError("Argument 'cell': expected 'tuple', got " + str(type(cell)))
        if len(cell) != 3:
            raise ValueError("Tuple 'cell' should have 3 elements, but has " + str(len(cell)))
        if type(cell[0]) != int or type(cell[1]) != int or type(cell[2]) != int:
            raise TypeError("Argument 'cell' should be a tuple of integers")
        if not 0 <= cell[0] < self.__gridSize and 0 <= cell[1] < self.__gridSize and 0 <= cell[2] < self.__gridSize:
            raise TypeError("Argument 'cell' should be a tuple of integers between 1 and the grid size")
        self.__gui.highlight_played_cell(cell)

    def send_state_matrix(self, matrix):
        self.__gui.stateMatrix = matrix

    def stop(self):
        print("Gui stop function")
        self.__boolContinue = False
        try:
            pygame.event.post(pygame.event.Event(QUIT))
        except:
            pass
        try:
            self.__lockEvent.release()
        except:
            pass





















