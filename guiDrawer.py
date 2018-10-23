from __future__ import division

import pygame
from perspectiveprojection import Polygon

class Drawer:

    def __init__(self,screen):
        self.screen = screen

        self.colorHighlight = [255, 255, 0]
        self.color1 = [255, 0, 0]
        self.color2 = [0, 255, 0]
        self.colorBackground = [100, 100, 100]
        self.gridColor = [150, 150, 255]
        self.gridSelecColor = [255, 150, 255]
        self.gridLineColor = [0, 0, 100]

    def erase(self):
        self.screen.fill(self.colorBackground)  # Fill the screen (background color)

    def drawCell(self,cellPolygon,stateColor = 0):
        """Draws a cell taking the corresponding polygon and chose the color depending on the state"""
        pointsList = cellPolygon.xyProjected
        if stateColor == 0 :
            pygame.draw.polygon(self.screen, self.gridColor, pointsList)
        else :
            pygame.draw.polygon(self.screen, self.gridSelecColor, pointsList)
        pygame.draw.aalines(self.screen, self.gridLineColor, True, pointsList)

    def drawState(self,statePolygon,translation,stateColor):
        """Draws a cross or a circle corresponding to statePolygon (by translating it from the center)"""
        statePolygon.translate(translation)
        if stateColor == 1:
            pygame.draw.aalines(self.screen, self.color1, True, statePolygon.xyProjected)
        elif stateColor == 2:
            pygame.draw.aalines(self.screen, self.color2, True, statePolygon.xyProjected)
        statePolygon.translate(-np.array(translation).tolist())

    def highlightCell(self,cellPolygon):
        pygame.draw.lines(self.screen, self.colorHighlight, True,
                          cellPolygon.xyProjected, 4)


