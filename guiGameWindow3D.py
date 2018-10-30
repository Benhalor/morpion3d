#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Class GameWindow3D, handling the displaying properties of the 3D grid and its state, and also handling the interaction
between the user and the grid (cell selection and grid rotation)
"""

from guiDrawer import Drawer
from perspectiveprojection import *


class GameWindow3D:

    def __init__(self, parentWindow, gridWidth=10, gridSize=3):
        """Takes as input the parentWindow (instance of MainWindow), the true width (in 3D) of the grid
        and the grid size (number of cells for one row or one column)"""

        if type(gridWidth) != int:
            raise TypeError("Argument 'gridWidth': expected 'int', got " + str(type(gridWidth)))
        if gridWidth < 1:
            raise ValueError("Argument 'gridWidth' should be greater than 1")
        if type(gridSize) != int:
            raise TypeError("Argument 'gridSize': expected 'int', got " + str(type(gridSize)))
        if not 3 <= gridSize <= 9:
            raise ValueError("Argument 'gridSize' should be between 3 and 9, got " + str(gridSize))

        self.__parentWindow = parentWindow  # Parent window (instance of MainWindow)
        self.__drawer = Drawer(parentWindow.screen)  # Drawer object to draw the polygons with pygame

        self.__gridSize = gridSize  # Size of the grid (default = 3)
        self.__gridWidth = gridWidth  # Overall width of the grid (real 3d width)
        self.__cellSize = gridWidth / gridSize  # Width of a cell of the grid (real 3D width)
        self.__heightSeparation = 22 / self.__gridSize  # Distance between each plane (real 3D distance)

        self.__stateMatrix = np.zeros([self.__gridSize, self.__gridSize, self.__gridSize])  # Matrix containing
        # the states of each cell (0 = empty, 1 = player1, 2 = opponent)

        self.__coloringMatrix = np.zeros([self.__gridSize, self.__gridSize, self.__gridSize])  # Matrix containing the
        # color of each cell (0 = normal, 2 = winning cells)

        self.__selectedCell = (-1, -1, -1)  # Coordinates of the selected cell ([-1,-1,-1] if no cell is selected)

        self.__space = Space()  # Space which will contain all the points and polygons defining the grid
        ax, ay, az = self.__space.angles

        # Script to define all the points of the grid 4 points for each cell
        self.__points = [[[None for k in range(self.__gridSize)] for j in range(self.__gridSize + 1)] for i in
                         range(self.__gridSize + 1)]
        for i in range(self.__gridSize + 1):
            for j in range(self.__gridSize + 1):
                for k in range(self.__gridSize):
                    xp = -self.__gridWidth / 2 + i * self.__cellSize
                    yp = -self.__gridWidth / 2 + j * self.__cellSize
                    zp = (-k + (self.__gridSize - 1) // 2) * self.__heightSeparation
                    self.__points[i][j][k] = Point(self.__space, xp, yp, zp)

        # Script to define all the polygons formed by these points (one polygon for each cell)
        self.__polygons = [[[None for k in range(self.__gridSize)] for j in range(self.__gridSize)] for i in
                           range(self.__gridSize)]
        for i in range(self.__gridSize):
            for j in range(self.__gridSize):
                for k in range(self.__gridSize):
                    P1 = self.__points[i][j][k]
                    P2 = self.__points[i + 1][j][k]
                    P3 = self.__points[i][j + 1][k]
                    P4 = self.__points[i + 1][j + 1][k]
                    self.__polygons[i][j][k] = Polygon(self.__space, [P1, P2, P4, P3],
                                                       name='cell' + str(i) + str(j) + str(k))

        # Script to create a polygon defining a Cross (which will be drawn in the grid during the game)
        C1 = Point(self.__space, 0, 0, 0)
        C2 = Point(self.__space, -self.__cellSize / 2.5, -self.__cellSize / 2.5, 0)
        C3 = Point(self.__space, self.__cellSize / 2.5, self.__cellSize / 2.5, 0)
        C4 = Point(self.__space, 0, 0, 0)
        C5 = Point(self.__space, -self.__cellSize / 2.5, self.__cellSize / 2.5, 0)
        C6 = Point(self.__space, self.__cellSize / 2.5, -self.__cellSize / 2.5, 0)
        self.__crossPolygon = Polygon(self.__space, [C1, C2, C3, C4, C5, C6], name="cross", locate=False)

        # Script to create a polygon defining a Circle (which will be drawn in the grid during the game)
        circle = []
        for i in range(10):
            circle.append(Point(self.__space, self.__cellSize / 2.5 * np.cos(2 * np.pi * i / 10),
                                self.__cellSize / 2.5 * np.sin(2 * np.pi * i / 10),
                                0))
        self._circlePolygon = Polygon(self.__space, circle, name="circle", locate=False)

        self.__space.angles = (ax - 0.25, ay + 0.25, az + 0.05)

    # ================ EVENT MANAGEMENT METHODS =============================

    def move(self, direction, speed):
        """Rotates the grid in the specified direction and with the corresponding speed"""

        if type(direction) != str:
            raise TypeError("Argument 'direction': expected str, got " + str(type(direction)))
        if direction not in ["left", "right", "up", "down"]:
            raise ValueError("Argument 'direction': expected values 'left', 'right', 'up' or 'down', got "
                             + str(direction))
        if type(speed) != float:
            raise TypeError("Argument 'speed': expected float, got " + str(type(speed)))
        if speed <= 0:
            raise ValueError("Argument 'speed' should be strictly positive, got " + str(speed))

        ax, ay, az = self.__space.angles
        if direction == "left":
            az -= speed
        elif direction == "right":
            az += speed
        elif direction == "up":
            ax -= speed
        elif direction == "down":
            ax += speed
        self.__space.angles = (ax, ay, az)
        self.__parentWindow.update_screen()

    def detect_cell_pos(self, mousePos):
        """Changes the cell coordinates to the ones corresponding to the mouse position ([-1,-1,-1] = out)"""
        cellPos = (-1, -1, -1)
        ((xmin, ymin), (xmax, ymax)) = self.__space.xyBounds # Get the bounds of the grid in the screen to call the
        # following script only if the mouse is on the grid.
        if (xmin <= mousePos[0] <= xmax) and (ymin <= mousePos[1] <= ymax):
            detectedPolygon = self.__space.locate_polygon(mousePos[0], mousePos[1])
            if detectedPolygon is not None:
                cellPos = (int(detectedPolygon.name[4]), int(detectedPolygon.name[5]), int(detectedPolygon.name[6]))
            self.__selectedCell = cellPos

    # ================ DRAWING METHODS ======================================

    def draw_grid(self):
        """Draw all the cells of the morpion, then draw the state of the  th"""

        self.__drawer.erase()
        for poly in reversed(self.__space.polygons):
            name = poly.name
            if len(name) >= 4 and name[:4] == "cell":
                i = int(name[4])
                j = int(name[5])
                k = int(name[6])
                self.__drawer.draw_cell(poly, 1 if (i, j, k) == self.__selectedCell else self.__coloringMatrix[i,j,k])
                if self.__stateMatrix[i, j, k] != 0:
                    translation = (-self.__gridWidth / 2 + (i + 1 / 2) * self.__cellSize,
                                   -self.__gridWidth / 2 + (j + 1 / 2) * self.__cellSize,
                                   (-k + (self.__gridSize - 1) // 2) * self.__heightSeparation)
                    if self.__stateMatrix[i, j, k] == 1:
                        self.__drawer.draw_state(self._circlePolygon, translation, 1)
                    elif self.__stateMatrix[i, j, k] == 2:
                        self.__drawer.draw_state(self.__crossPolygon, translation, 2)
        if self.__selectedCell != (-1, -1, -1):
            i, j, k = self.__selectedCell
            self.__drawer.highlight_cell(self.__polygons[i][j][k])

    def update_screen(self):
        self.draw_grid()

    # ============== METHODS RELATED TO INTERACTION WITH GAME ENGINE =============

    def highlight_winning_cell(self,cell):
        """Change the color of the winning cells"""
        if type(cell) != tuple:
            raise TypeError("Argument 'cell': expected 'tuple', got " + str(type(cell)))
        if len(cell) != 3:
            raise ValueError("Tuple 'cell' should have 3 elements, but has " + str(len(cell)))
        if type(cell[0]) != int or type(cell[1]) != int or type(cell[2]) != int:
            raise TypeError("Argument 'cell' should be a tuple of integers")
        if not 0 <= cell[0] < self.__gridSize and 0 <= cell[1] < self.__gridSize and 0 <= cell[2] < self.__gridSize:
            raise TypeError("Argument 'cell' should be a tuple of integers between 1 and the grid size")
        self.__coloringMatrix[cell] = 2
        self.__parentWindow.update_screen()

    def __get_state_matrix(self):
        return self.__stateMatrix

    def __set_state_matrix(self, newStateMatrix):
        self.__stateMatrix = np.array(newStateMatrix)
        self.__stateMatrix = self.__stateMatrix.astype(int)
        self.__parentWindow.update_screen()

    def __get_played_cell(self):
        cell = self.__selectedCell
        self.__selectedCell = (-1, -1, -1)
        self.__parentWindow.update_screen()
        return cell

    stateMatrix = property(__get_state_matrix, __set_state_matrix)
    playedCell = property(__get_played_cell)
