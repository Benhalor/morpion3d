from __future__ import division

import pygame
from guiGameWindow3D import GameWindow3D

from pygame.locals import *


class MainWindow:

    def __init__(self, gridSize):
        self.__gridSize = gridSize
        self.__wantToPlay = False
        self.__cell = (-1, -1, -1)
        self.__screen = None
        self.__gui = None

        self.__textMessage = " "

        self.__boolMoveLeft = False
        self.__boolMoveRight = False
        self.__boolMoveUp = False
        self.__boolMoveDown = False
        self.__boolRightClick = False
        
        pygame.init()
        self.__alive = True
        
        self.__screen = pygame.display.set_mode((640, 480))
        self.__gui = GameWindow3D(self, 10, self.__gridSize)

        self.__textMessage = "New window started."

        self.update_screen()
        
        # Event management
        pygame.event.clear()
        
        print("GUI: init")

    def run(self):
        if not self.__alive:
            return 0
        
        startingTime = pygame.time.get_ticks()
        #print(startingTime)
        
        # Rotate view
        if self.__boolMoveLeft or self.__boolMoveRight or self.__boolMoveUp or self.__boolMoveDown or self.__boolRightClick:
            if self.__boolMoveLeft:
                self.__gui.move("left", 0.07)
            elif self.__boolMoveRight:
                self.__gui.move("right", 0.07)
            elif self.__boolMoveUp:
                self.__gui.move("up", 0.07)
            elif self.__boolMoveDown:
                self.__gui.move("down", 0.07)
            elif self.__boolRightClick:
                x = pygame.mouse.get_pos()[0]
                if x < 200:
                    self.__gui.move("left", 0.001 * (200 - x))
                elif x > 400:
                    self.__gui.move("right", 0.001 * (x - 400))
        #self.__gui.step()
        self.update_screen()

        boolTime = True
        while boolTime and self.__alive:
            if pygame.event.peek():
                e = pygame.event.poll()
                
                # View rotation
                if e.type == KEYDOWN:
                    if e.key == K_LEFT:
                        self.__boolMoveLeft = True
                    elif e.key == K_RIGHT:
                        self.__boolMoveRight = True
                    elif e.key == K_UP:
                        self.__boolMoveUp = True
                    elif e.key == K_DOWN:
                        self.__boolMoveDown = True
                if e.type == KEYUP:
                    if e.key == K_LEFT:
                        self.__boolMoveLeft = False
                    elif e.key == K_RIGHT:
                        self.__boolMoveRight = False
                    elif e.key == K_UP:
                        self.__boolMoveUp = False
                    elif e.key == K_DOWN:
                        self.__boolMoveDown = False
    
                if e.type == MOUSEBUTTONDOWN:
                    if e.button == 1 and self.__wantToPlay:  # If left click, select cell if it is your turn
                        cell = self.__gui.playedCell
                        #if cell != (-1, -1, -1):
                        self.__cell = cell
                            
                    elif e.button == 3:
                        self.__boolRightClick = True
                if e.type == MOUSEBUTTONUP:
                    if e.button == 3:  # If right click
                        self.__boolRightClick = False
                if e.type == MOUSEMOTION:
                    self.__gui.detect_cell_pos(e.pos)
                if e.type == QUIT:
                    print("GUI: Event quit", e)
                    self.stop()
                    pygame.quit()
            boolTime = pygame.time.get_ticks() - startingTime < 30

    def update_screen(self):
        if self.__alive:
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
        #self.__lockEvent.acquire()
        #self.__lockEvent.release()

        self.__wantToPlay = True
        #self.__cell = None
        #self.__lockEvent.acquire()

        # Wait the run loop to release the lock (only when cell is clicked)
        #self.__lockEvent.acquire()
        #self.__lockEvent.release()
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
        print("GUI: stop")
        pygame.quit()
        self.__alive = False
        print("GUI: end")
        
    def __get_alive(self):
        return self.__alive
    alive = property(__get_alive)





















