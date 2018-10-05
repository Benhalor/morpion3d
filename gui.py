# Import library
import pygame
import time

from pygame.locals import *


class GameWindow:

    def __init__(self):
        pygame.init()  # Initialization of the library

        self.screen = pygame.display.set_mode((640, 480))  # Creation of the window object

        start = time.time()

        fond = pygame.image.load("graphics/backgroundTest.jpg").convert()
        self.screen.blit(fond, (0, 0))
        self.screen.fill([10, 10, 70])

        self.gridWidth = 300
        self.cellSize = self.gridWidth/3
        self.gridPos = [10,10]
        self.cellPos = [self.gridPos[0]+int(self.cellSize/2),self.gridPos[1]+int(self.cellSize/2)]

        pygame.draw.circle(self.screen, [10,200,200], self.cellPos,25,2)
        pygame.draw.rect(self.screen, [255,255,255], self.gridPos+[self.gridWidth,self.gridWidth],2)
        pygame.draw.rect(self.screen, [255, 255, 255],[self.gridPos[0], self.gridPos[1]+self.cellSize] + [self.gridWidth, self.cellSize], 2)
        pygame.draw.rect(self.screen, [255, 255, 255],[self.gridPos[0]+ self.cellSize, self.gridPos[1]] + [self.cellSize,self.gridWidth], 2)
        pygame.display.flip()

        end = time.time()
        # Boucle infinie
        while end - start < 2:
            end = time.time()


window1 = GameWindow()
