from __future__ import division

import pygame
from perspectiveprojection import Polygon
import numpy as np


class Drawer:

    def __init__(self, screen):
        self._screen = screen #Gets the pygame screen to draw on it

        self._colorHighlight = [255, 255, 0] #Color of the border of a cell to highlight
        self._color1 = [255, 0, 0] #Color of the cross of the first player
        self._color2 = [0, 255, 0] #Color of the circle of the opponent
        self._colorBackground = [100, 100, 100] #Color of the screen background
        self._gridColor = [150, 150, 255]  #Color of the lines of the grid
        self._gridSelectColor = [255, 150, 255] #Color to fill a selected cell
        self._gridLineColor = [0, 0, 100] #Color to fill the grid

    def erase(self):
        self._screen.fill(self._colorBackground)  # Fill the screen (background color)

    def draw_cell(self, cellPolygon, stateColor=0):
        """Draws a cell taking the corresponding polygon and chose the color depending on the state"""
        pointsList = cellPolygon.xyProjected
        if stateColor == 0:
            pygame.draw.polygon(self._screen, self._gridColor, pointsList)
        else:
            pygame.draw.polygon(self._screen, self._gridSelectColor, pointsList)
        pygame.draw.aalines(self._screen, self._gridLineColor, True, pointsList)

    def draw_state(self, statePolygon, translation, stateColor):
        """Draws a cross or a circle corresponding to statePolygon (by translating it from the center using translation)"""
        statePolygon.translate(translation)
        if stateColor == 1:
            pygame.draw.aalines(self._screen, self._color1, True, statePolygon.xyProjected)
        elif stateColor == 2:
            pygame.draw.aalines(self._screen, self._color2, True, statePolygon.xyProjected)
        statePolygon.translate(-np.array(translation).tolist())

    def highlight_cell(self, cellPolygon):
        pygame.draw.lines(self._screen, self._colorHighlight, True,
                          cellPolygon.xyProjected, 4)
