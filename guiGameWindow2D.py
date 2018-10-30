#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Class GameWindow2D, handling the displaying properties of the 2D grid and its state, and also handling the interaction
between the user and the grid (cell selection and grid rotation)

"""

from guiDrawer import Drawer
from perspectiveprojection import *


class GameWindow2D:

    def __init__(self, parentWindow, gridWidth, gridSize):
        """Takes as input the parentWindow (instance of MainWindow), the pixel width of the grid
        and the grid size (number of cells for one row or one column)"""

        self.__parentWindow = parentWindow
        self.__drawer = Drawer(parentWindow.screen)
        
        self.__gridSize = gridSize  # Size of the grid (default = 3)
        self.__gridWidth = gridWidth  # gridWidth  # Overall pixel width of the grid
        self.__cellSize = gridWidth / gridSize
        
        self.__stateMatrix = np.zeros([self.__gridSize, self.__gridSize])
        self.__coloringMatrix = np.zeros([self.__gridSize, self.__gridSize])

        self.__selectedCell = (-1, -1)  # Coordinates of the selected cell ([-1,-1] if no cell is selected)

        self.__space = Space()
        
        # Cells points
        self.__points = [[None for j in range(self.__gridSize + 1)] for i in range(self.__gridSize + 1)]

        for i in range(self.__gridSize + 1):
            for j in range(self.__gridSize + 1):
                xp = -self.__gridWidth / 2 + i * self.__cellSize
                yp = -self.__gridWidth / 2 + j * self.__cellSize
                self.__points[i][j][k] = Point(self.__space, xp, yp, 0)
        
        # Cells polygons
        self.__polygons = [[None for j in range(self.__gridSize)] for i in range(self.__gridSize)]
        for i in range(self.__gridSize):
            for j in range(self.__gridSize):
                P1 = self.__points[i][j]
                P2 = self.__points[i + 1][j]
                P3 = self.__points[i][j + 1]
                P4 = self.__points[i + 1][j + 1]
                self.__polygons[i][j] = Polygon(self.__space, [P1, P2, P4, P3], name ='cell' + str(i) + str(j))
    
        # Cross
        C1 = Point(self.__space, 0, 0, 0)
        C2 = Point(self.__space, -self.__cellSize / 2.5, -self.__cellSize / 2.5, 0)
        C3 = Point(self.__space, self.__cellSize / 2.5, self.__cellSize / 2.5, 0)
        C4 = Point(self.__space, 0, 0, 0)
        C5 = Point(self.__space, -self.__cellSize / 2.5, self.__cellSize / 2.5, 0)
        C6 = Point(self.__space, self.__cellSize / 2.5, -self.__cellSize / 2.5, 0)
        self.__crossPolygon = Polygon(self.__space, [C1, C2, C3, C4, C5, C6], name ="cross", locate = False)
        
        
        circle = []
        for i in range(10):
            circle.append(Point(self.__space, self.__cellSize / 2.5 * np.cos(2 * np.pi * i / 10),
                                self.__cellSize / 2.5 * np.sin(2 * np.pi * i / 10),
                                0))
        self._circlePolygon = Polygon(self.__space, circle, name ="circle", locate = False)
        
        self.__space.angles = (0,0,0)
        self.__space.axes = ((1,0,0), (0,-1,0), (0,0,-1))

    # ================ EVENT MANAGEMENT METHODS =============================

    def detect_cell_pos(self, mousePos):
        """Changes the cell coordinates corresponding to the mouse position ([-1,-1] = out of the grid)"""
        cellPos = (-1, -1)
        xmin = -self.__gridWidth / 2
        xmax = -self.__gridWidth / 2 + self.__gridSize * self.__cellSize
        if (xmin <= mousePos[0] <= xmax) and (xmin <= mousePos[1] <= xmax) :
            detectedPolygon = self.__space.locate_polygon(mousePos[0], mousePos[1])
            if detectedPolygon is not None:
                cellPos = (int(detectedPolygon.name[4]), int(detectedPolygon.name[5]))
            self.__selectedCell = cellPos

            self.__parentWindow.textMessage = str(self.__selectedCell[0]) + str(self.__selectedCell[1])

    # ================ DRAWING METHODS ======================================

    def draw_grid(self):
        """Draw all the edges of the morpion grid taking into account the grid position and its size"""

        self.__drawer.erase()
        for poly in reversed(self.__space.polygons):
            name = poly.name
            if len(name) >= 4 and name[:4] == "cell":
                i = int(name[4])
                j = int(name[5])
                self.__drawer.draw_cell(poly, 1 if (i, j) == self.__selectedCell else 0)
                if self.__stateMatrix[i, j] != 0:
                    translation = (-self.gridWidth / 2 + (i + 1 / 2) * self.__cellSize,
                                       -self.gridWidth / 2 + (j + 1 / 2) * self.__cellSize,
                                       0)
                    if self.__stateMatrix[i, j] == 1:
                        self.__drawer.draw_state(self._circlePolygon, translation, 1)
                    elif self.__stateMatrix[i, j] == 2:
                        self.__drawer.draw_state(self.__crossPolygon, translation, 2)
        if self.__selectedCell != (-1, -1):
            i,j = self.__selectedCell
            self.__drawer.highlight_cell(self.__polygons[i][j])
                
    def update_screen(self):
        self.draw_grid()
        # self.draw_selected_cell()
        # self.draw_current_state()

    # ============== METHODS RELATED TO DISPLAYING PROPERTIES =============

    def __get_grid_width(self):
        return self.__gridWidth

    def __get_grid_size(self):
        return self.__gridSize

    def __get_state_matrix(self):
        return self.__stateMatrix

    def __set_state_matrix(self, newStateMatrix):
        self.__stateMatrix = np.array(newStateMatrix)
        self.__stateMatrix = self.__stateMatrix.astype(int)
        self.__parentWindow.update_screen()
        
    def __get_played_cell(self):
        """Returns the cell coordinates and reinitialize selectedCell to [-1,-1]"""
        cell = self.__selectedCell
        self.__selectedCell = (-1, -1)
        self.__parentWindow.update_screen()
        return cell

    gridWidth = property(__get_grid_width)
    gridSize = property(__get_grid_size)
    stateMatrix = property(__get_state_matrix, __set_state_matrix)
    playedCell = property(__get_played_cell)
