#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import division

import pygame

class Drawer:

    def __init__(self, screen):
        self.__screen = screen  # Gets the pygame screen to draw on it

        self.__colorHighlight = [255, 255, 0]  # Color of the border of a cell to highlight
        self.__color1 = [255, 0, 0]  # Color of the cross of the first player
        self.__color2 = [0, 255, 0]  # Color of the circle of the opponent
        self.__colorBackground = [100, 100, 100]  # Color of the screen background
        self.__gridColor = [150, 150, 255]  # Color of the lines of the grid
        self.__gridSelectColor = [255, 150, 255]  # Color to fill a selected cell
        self.__gridLineColor = [0, 0, 100]  # Color to fill the grid

    def erase(self):
        self.__screen.fill(self.__colorBackground)  # Fill the screen (background color)

    def draw_cell(self, cellPolygon, stateColor=0):
        """Draws a cell taking the corresponding polygon and chose the color depending on the state"""
        pointsList = cellPolygon.xyProjected
        if stateColor == 0:  # If the cell is unselected
            pygame.draw.polygon(self.__screen, self.__gridColor, pointsList)
        else:  # if the cell is selected
            pygame.draw.polygon(self.__screen, self.__gridSelectColor, pointsList)
        pygame.draw.aalines(self.__screen, self.__gridLineColor, True, pointsList)  # Draws the lines of the grid

    def draw_state(self, statePolygon, translation, stateColor):
        """Draws a cross or a circle corresponding to statePolygon (by translating it from the center using translation)"""
        statePolygon.translate(translation)
        if stateColor == 1:
            pygame.draw.aalines(self.__screen, self.__color1, True, statePolygon.xyProjected)
        elif stateColor == 2:
            pygame.draw.aalines(self.__screen, self.__color2, True, statePolygon.xyProjected)
        statePolygon.translate((-translation[0], -translation[1], -translation[2]))

    def highlight_cell(self, cellPolygon):
        pygame.draw.lines(self.__screen, self.__colorHighlight, True,
                          cellPolygon.xyProjected, 4)
