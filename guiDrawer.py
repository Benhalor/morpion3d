#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Class Drawer, handling the drawing of the background and the 3d grid using Pygame
"""

import pygame


class Drawer:

    def __init__(self, screen):
        self.__screen = screen  # Gets the pygame screen to draw on it
        self.__backgroundImage = pygame.image.load('graphics/metal.jpg')
        self.__colorHighlight = [255, 255, 0]  # Color of the border of a cell to highlight
        self.__color1 = [200, 0, 0]  # Color of the cross of the first player
        self.__color2 = [0, 200, 0]  # Color of the circle of the opponent
        self.__colorBackground = [100, 100, 100]  # Color of the screen background
        self.__gridColor = [150, 150, 255]  # Color of the lines of the grid
        self.__gridSelectColor = [255, 150, 255]  # Color to fill a selected cell
        self.__gridWinningColor = [0, 0, 255]  # Color to fill the winning cells at the end
        self.__gridPlayedColor = [200, 150, 255]  # Color to fill the cell which was played in the last turn
        self.__gridLineColor = [0, 0, 100]  # Color of the lines the grid

    def erase(self):
        self.__screen.fill(self.__colorBackground)  # Fill the screen (background color)
        self.__screen.blit(self.__backgroundImage,(0,0))

    def draw_cell(self, cellPolygon, stateColor=0):
        """Draws a cell taking the corresponding polygon and chose the color depending on the state"""
        pointsList = cellPolygon.xyProjected
        if stateColor == 0:  # If the cell is unselected
            pygame.draw.polygon(self.__screen, self.__gridColor, pointsList)
        elif stateColor == 1:  # if the cell is selected
            pygame.draw.polygon(self.__screen, self.__gridSelectColor, pointsList)
        elif stateColor == 2:
            pygame.draw.polygon(self.__screen, self.__gridWinningColor, pointsList)
        elif stateColor == 3:
            pygame.draw.polygon(self.__screen, self.__gridPlayedColor, pointsList)
        pygame.draw.aalines(self.__screen, self.__gridLineColor, True, pointsList)  # Draws the lines of the grid

    def draw_cross(self, crossPolygon):
        """Draw a cross"""
        pygame.draw.polygon(self.__screen, self.__color2, crossPolygon.xyProjected)
    
    def draw_circle(self, circlePolygon):
        """Draw a cross"""
        pygame.draw.polygon(self.__screen, self.__color1, circlePolygon.xyProjected)
    
    def draw_state(self, statePolygon, translation, stateColor):
        """Draws a cross or a circle corresponding to statePolygon (by translating it from the center using translation)"""
        statePolygon.translate(translation)
        if stateColor == 1:
            pygame.draw.aalines(self.__screen, self.__color1, True, statePolygon.xyProjected)
        elif stateColor == 2:
            pygame.draw.aalines(self.__screen, self.__color2, True, statePolygon.xyProjected)
        statePolygon.translate((-translation[0], -translation[1], -translation[2]))

    def highlight_cell(self, cell):
        for poly in cell.polygons:
            pygame.draw.lines(self.__screen, self.__colorHighlight, True, poly.xyProjected, 4)

    #def draw(self, )