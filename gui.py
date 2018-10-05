# Import library
import pygame
import time

from pygame.locals import *


class GameWindow:

    def __init__(self):
        pygame.init()  # Initialization of the library

        self.screen = pygame.display.set_mode((640, 480))  # Creation of the window object

        start = time.time() #Time measurement

        fond = pygame.image.load("graphics/backgroundTest.jpg").convert()
        self.screen.blit(fond, (0, 0)) #Draw an image at the position 0,0
        self.screen.fill([10, 10, 70]) #Fill the screen (background color)

        self.gridWidth = 300 #Overall width of the grid (can be modified)
        self.cellSize = self.gridWidth/3 #Size of a cell depending on the grid width
        self.gridPos = [10,10] #Position of the top left corner of the grid
        self.cellPos = [self.gridPos[0]+int(self.cellSize/2),self.gridPos[1]+int(self.cellSize/2)] #Position of the center of the top left circle

        self.drawGrid()

        pygame.draw.circle(self.screen, [10,200,200], self.cellPos,25,2)
        pygame.display.flip()

        end = time.time()
        # Boucle infinie
        while end - start < 20:
            end = time.time()

    def drawGrid(self):
        """Draw all the edges of the morpion grid taking into account the grid position and its size"""
        pygame.draw.rect(self.screen, [255, 255, 255], self.gridPos + [self.gridWidth, self.gridWidth], 2)
        pygame.draw.rect(self.screen, [255, 255, 255],
                         [self.gridPos[0], self.gridPos[1] + self.cellSize] + [self.gridWidth, self.cellSize], 2)
        pygame.draw.rect(self.screen, [255, 255, 255],
                         [self.gridPos[0] + self.cellSize, self.gridPos[1]] + [self.cellSize, self.gridWidth], 2)

    def drawCurrentState(self, matrix):
        """Draw the current state of the grid, (all the circles) taking into account an input state matrix (3x3)"""
        a = 0


window1 = GameWindow()
