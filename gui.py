# Import library
import pygame
import time
import numpy as np

from pygame.locals import *



class GameWindow2D:

    def __init__(self,gridWidth,gridPos):
        """Take as input the size of the grid and the position (tuple of 2 elements) of the top left corner of the grid"""
        pygame.init()  # Initialization of the library
        self.screen = pygame.display.set_mode((640, 480))  # Creation of the window object

        self._gridWidth = gridWidth  # Overall width of the grid (can be modified)
        self._gridPos = gridPos # Position of the top left corner of the grid
        self.compute_grid_properties()

        self.updateScreen()

        boolContinue = True
        #Event management
        while boolContinue:
            for event in pygame.event.get():
                if event.type == QUIT:
                    boolContinue = False
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:  # If left click
                        self.gridPos = event.pos
                        self.updateScreen()

    #================DRAWING METHODS======================================

    def drawGrid(self):
        """Draw all the edges of the morpion grid taking into account the grid position and its size"""
        fond = pygame.image.load("graphics/backgroundTest.jpg").convert()
        self.screen.blit(fond, (0, 0))  # Draw an image at the position 0,0
        self.screen.fill([10, 10, 70])  # Fill the screen (background color)
        pygame.draw.rect(self.screen, [255, 255, 255], self.gridPos + [self.gridWidth, self.gridWidth], 2)
        pygame.draw.rect(self.screen, [255, 255, 255],
                         [self.gridPos[0], self.gridPos[1] + self.cellSize] + [self.gridWidth, self.cellSize], 2)
        pygame.draw.rect(self.screen, [255, 255, 255],
                         [self.gridPos[0] + self.cellSize, self.gridPos[1]] + [self.cellSize, self.gridWidth], 2)

    def drawCurrentState(self, matrix):
        """Draw the current state of the grid, (all the circles) taking into account an input state matrix (3x3)"""
        for i in range(np.size(matrix,0)) :
            for j in range(np.size(matrix,1)) :
                if matrix[i,j]!=0 :
                    pos = [self.cellPos[0]+i*self.cellSize,self.cellPos[1]+j*self.cellSize]
                    if matrix[i,j] == 1 :
                        pygame.draw.circle(self.screen, [10, 200, 200],pos, 25, 2)
                    elif matrix[i,j] == 2 :
                        pygame.draw.circle(self.screen, [200, 10, 200], pos, 25, 2)

    def updateScreen(self):
        self.drawGrid()
        self.drawCurrentState(np.array([[1, 2, 0], [1, 1, 2], [0, 0, 1]]))
        pygame.display.flip()

    #============== METHODS RELATED TO DISPLAYING PROPERTIES =============

    def compute_grid_properties(self):
        self.cellSize = int(self.gridWidth / 3)  # Size of a cell depending on the grid width
        self.cellPos = [self.gridPos[0] + int(self.cellSize / 2),
                        self.gridPos[1] + int(self.cellSize / 2)]  # Position of the center of the top left circle

    def _get_grid_width(self):
        return self._gridWidth

    def _set_grid_width(self, newGridWidth):
        self._gridWidth = newGridWidth
        self.compute_grid_properties()
        # Position of the top left corner of the grid

    def _get_grid_pos(self):
        return self._gridPos

    def _set_grid_pos(self, newGridPos):
        self._gridPos = list(newGridPos)
        self.compute_grid_properties()

    gridWidth = property(_get_grid_width,_set_grid_width)
    gridPos = property(_get_grid_pos, _set_grid_pos)

window1 = GameWindow2D(300,[100,100])
