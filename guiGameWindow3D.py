#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Class GameWindow3D, handling the displaying properties of the 3D grid and its state, and also handling the interaction
between the user and the grid (cell selection and grid rotation)

Cell, Cross and Circle: subclasses of Mesh, used to display things
"""

import numpy as np
from random import uniform

import pygame
from perspectiveprojection import Point, Space, Polygon, Mesh


class Drawer:
    """
    Class Drawer, handling the drawing of the background and the 3d grid using Pygame
    """

    def __init__(self, screen):
        self.__screen = screen  # Gets the pygame screen to draw on it
        self.__colorHighlight = [255, 255, 0]  # Color of the border of a cell to highlight
        self.__gridLineColor = [0, 0, 100]  # Color of the lines the grid

    def draw_polygon(self, polygon, colorCoeff = 1):
        pygame.draw.polygon(self.__screen, (colorCoeff*polygon.mesh.color[0],
                                            colorCoeff * polygon.mesh.color[1],
                                            colorCoeff * polygon.mesh.color[2]), polygon.xyProjected)
        pygame.draw.aalines(self.__screen, self.__gridLineColor, True, polygon.xyProjected)

    def highlight_cell(self, cell):
        for poly in cell.polygons:
            pygame.draw.lines(self.__screen, self.__colorHighlight, True, poly.xyProjected, 4)


class GameWindow3D:
    """A window managed with pygame

    Attributes:
        screen (pygame.Surface): the pygame screen
        testMessage (str): This string is displayed in the bottom left corner (read/write)

    """

    def __init__(self, data):
        """Takes as input the true width (in 3D) of the grid
        and the grid size (number of cells for one row or one column)"""

        self.__data = data
        self.__drawer = Drawer(self.__data.window.screen)  # Drawer object to draw the polygons with pygame

        self.__gridSize = self.__data.gameSize  # Size of the grid (default = 3)
        self.__gridWidth = 10  # Overall width of the grid (real 3d width)
        self.__heightSeparation = 22 / self.__gridSize  # Distance between each plane (real 3D distance)

        self.__stateMatrix = np.zeros([self.__gridSize, self.__gridSize, self.__gridSize])  # Matrix containing
        # the states of each cell (0 = empty, 1 = player1, 2 = opponent)

        self.__selectedCell = (-1, -1, -1)  # Coordinates of the selected cell ([-1,-1,-1] if no cell is selected)

        # Space which will contain all the points and polygons defining the grid
        self.__space = Space()

        # Create the cells
        self.__cells = [[[None for k in range(self.__gridSize)] for j in range(self.__gridSize)] for i in
                        range(self.__gridSize)]

        self.__cellSize = 10 / self.__gridSize  # Width of a cell of the grid (real 3D width)

        for i in range(self.__gridSize):
            for j in range(self.__gridSize):
                for k in range(self.__gridSize):
                    xp = -self.__gridWidth / 2 + i * self.__cellSize
                    yp = -self.__gridWidth / 2 + j * self.__cellSize
                    zp = (-k + (self.__gridSize - 1) / 2) * self.__heightSeparation
                    self.__cells[i][j][k] = Cell(self.__space, xp, yp, zp, self.__cellSize, self.__heightSeparation / 10, (i, j, k), lowConfig = self.__data.lowConfig)

        # Camera speeds
        self.__omegax = 0.0
        self.__omegay = 0.0
        self.__omegaz = 0.0
        
        # Create a big circle. Its only purpose is cosmetic. This is disabled in the low graphics configuration
        if not self.__data.lowConfig:
            self.__bigCircle = BigCircle(self.__space, 1.05 * (self.__gridSize - 1) * self.__heightSeparation, self.__heightSeparation / 10, self.__heightSeparation / 10)
        
        # Set the view in a confortable angle and update the space instance
        self.__space.angles = (1, 0, 0.85)
        
        self.__updateCount = 0

    # ================ EVENT MANAGEMENT METHODS =============================

    def detect_cell_pos(self, mousePos):
        """Changes the cell coordinates to the ones corresponding to the mouse position ((-1,-1,-1) = out)"""
        cellPos = (-1, -1, -1)
        detectedPolygon = self.__space.locate_polygon(mousePos[0], mousePos[1])
        if detectedPolygon is not None:
            cellPos = detectedPolygon.mesh.cellId
        self.__selectedCell = cellPos

    # ================ DRAWING METHODS ======================================

    def draw_polygons(self):
        """Draw all the polygons of the morpion, and highlight the selected cell"""
        for poly in reversed(self.__space.polygons):
            if self.__data.lowConfig:
                self.__drawer.draw_polygon(poly)
            else:
                if poly.normalVector is not None :
                    if poly.normalVector.depth <= 0 :
                        self.__drawer.draw_polygon(poly, poly.normalVector.color_coeff)
                else:
                    self.__drawer.draw_polygon(poly)
        if self.__selectedCell != (-1, -1, -1):
            i, j, k = self.__selectedCell
            self.__drawer.highlight_cell(self.__cells[i][j][k])

    def step(self):
        """Update the animations (camera view and others)"""
        if (self.__omegax != 0.0) or (self.__omegay != 0.0) or (self.__omegaz != 0.0):
            ax, ay, az = self.__space.angles
            ax += self.__omegax
            ay += self.__omegay
            az += self.__omegaz
            self.__space.angles = (ax, ay, az)
        else:
            if self.__updateCount >= 30:
                self.__space.update()
                self.__updateCount = 0
            else:
                self.__updateCount += 1
        if not self.__data.lowConfig:
            self.__bigCircle.step()

    # ============== METHODS RELATED TO INTERACTION WITH GAME SESSION =============

    def highlight_winning_cell(self, cellId):
        """Change the color of the winning cells"""
        if type(cellId) != tuple:
            raise TypeError("Argument 'cellId': expected 'tuple', got " + str(type(cellId)))
        if len(cellId) != 3:
            raise ValueError("Tuple 'cellId' should have 3 elements, but has " + str(len(cellId)))
        if type(cellId[0]) != int or type(cellId[1]) != int or type(cellId[2]) != int:
            raise TypeError("Argument 'cellId' should be a tuple of integers")
        i, j, k = cellId
        self.__cells[i][j][k].color = (0, 0, 255)

    def highlight_played_cell(self, cellId):
        """Change the color of the last played cell"""
        if type(cellId) != tuple:
            raise TypeError("Argument 'cellId': expected 'tuple', got " + str(type(cellId)))
        if len(cellId) != 3:
            raise ValueError("Tuple 'cellId' should have 3 elements, but has " + str(len(cellId)))
        if type(cellId[0]) != int or type(cellId[1]) != int or type(cellId[2]) != int:
            raise TypeError("Argument 'cellId' should be a tuple of integers")
        for xx in self.__cells:
            for yy in xx:
                for c in yy:
                    c.color = (150, 150, 255)
        i, j, k = cellId
        self.__cells[i][j][k].color = (200, 150, 255)

    def __get_state_matrix(self):
        return self.__stateMatrix

    def __set_state_matrix(self, newStateMatrix):
        """Set the new state matrix and place a cross or a circle if there is any change"""
        for i in range(self.__gridSize):
            for j in range(self.__gridSize):
                for k in range(self.__gridSize):
                    if newStateMatrix[i][j][k] != self.__stateMatrix[i][j][k]:
                        xp = -self.__gridWidth / 2 + (i + 0.5) * self.__cellSize
                        yp = -self.__gridWidth / 2 + (j + 0.5) * self.__cellSize
                        zp = (-k + (self.__gridSize - 1) / 2) * self.__heightSeparation
                        if newStateMatrix[i][j][k] == 1:
                            Circle(self.__space, xp, yp, zp, 0.45 * self.__cellSize, self.__heightSeparation / 10, lowConfig = self.__data.lowConfig)
                        elif newStateMatrix[i][j][k] == 2:
                            Cross(self.__space, xp, yp, zp, 0.45 * self.__cellSize, self.__heightSeparation / 10, lowConfig = self.__data.lowConfig)
                        self.__space.update()
        self.__stateMatrix = np.array(newStateMatrix)
        self.__stateMatrix = self.__stateMatrix.astype(int)

    stateMatrix = property(__get_state_matrix, __set_state_matrix)

    def __get_selected_cell(self):
        return self.__selectedCell

    selectedCell = property(__get_selected_cell)

    def __get_omegax(self):
        return self.__omegax

    def __set_omegax(self, o):
        if type(o) != float:
            raise TypeError("Argument 'o': expected 'float, got " + str(type(o)))
        self.__omegax = o

    omegax = property(__get_omegax, __set_omegax)

    def __get_omegay(self):
        return self.__omegay

    def __set_omegay(self, o):
        if type(o) != float:
            raise TypeError("Argument 'o': expected 'float, got " + str(type(o)))
        self.__omegay = o

    omegay = property(__get_omegay, __set_omegay)

    def __get_omegaz(self):
        return self.__omegaz

    def __set_omegaz(self, o):
        if type(o) != float:
            raise TypeError("Argument 'o': expected 'float, got " + str(type(o)))
        self.__omegaz = o

    omegaz = property(__get_omegaz, __set_omegaz)


class Cell(Mesh):
    """A mesh (a rectangular cuboid) representing a cell

    Attributes:
        cellId (3-tuple): an id giving the position of the cell with in-game coordinates (read only)
        color (3-tuple): the color the cell should be drawn (read/write)

    Note:
        Subclass from Mesh

    """

    def __init__(self, space, x, y, z, width, thickness, cellId, lowConfig = False):
        if type(x) != float:
            raise TypeError("Argument 'x': expected 'float', got " + str(type(x)))
        if type(y) != float:
            raise TypeError("Argument 'y': expected 'float', got " + str(type(y)))
        if type(z) != float:
            raise TypeError("Argument 'z': expected 'float', got " + str(type(z)))
        if type(width) != float:
            raise TypeError("Argument 'width': expected 'float', got " + str(type(width)))
        if type(thickness) != float:
            raise TypeError("Argument 'thickness': expected 'float', got " + str(type(thickness)))
        if not isinstance(space, Space):
            raise TypeError("Argument 'space' is not an instance of class 'Space'")
        A = Point(space, x, y, z - thickness / 2)
        B = Point(space, x + width, y, z - thickness / 2)
        C = Point(space, x + width, y + width, z - thickness / 2)
        D = Point(space, x, y + width, z - thickness / 2)
        P1 = Polygon(space, [A, B, C, D],True,(0,0,-1))
        if lowConfig:
            Mesh.__init__(self, space, [P1])
        else:
            E = Point(space, x, y, z + thickness / 2)
            F = Point(space, x + width, y, z + thickness / 2)
            G = Point(space, x + width, y + width, z + thickness / 2)
            H = Point(space, x, y + width, z + thickness / 2)
            P2 = Polygon(space, [B, C, G, F],True,(1,0,0))
            P3 = Polygon(space, [C, D, H, G],True,(0,1,0))
            P4 = Polygon(space, [H, E, A, D],True,(-1,0,0))
            P5 = Polygon(space, [F, E, A, B],True,(0,-1,0))
            P6 = Polygon(space, [E, F, G, H],True,(0,0,1))
            Mesh.__init__(self, space, [P1, P2, P3, P4, P5, P6])
        self.__cellId = cellId
        self.__color = (150, 150, 255)

    def __get_cell_id(self):
        return self.__cellId

    cellId = property(__get_cell_id)

    def __get_color(self):
        return self.__color

    def __set_color(self, c):
        if type(c) != tuple:
            raise TypeError("Argument 'c': expected 'tuple', got " + str(type(c)))
        if len(c) != 3:
            raise ValueError("Tuple c should have 3 elements, but has " + str(len(c)))
        self.__color = c

    color = property(__get_color, __set_color)


class Cross(Mesh):
    """A mesh representing a cross

    Attributes:
        color (3-tuple): RGB color of the circle (read only)

    Note:
        Subclass from Mesh

    """

    def __init__(self, space, x, y, z, radius, thickness, lowConfig = False):
        if type(x) != float:
            raise TypeError("Argument 'x': expected 'float', got " + str(type(x)))
        if type(y) != float:
            raise TypeError("Argument 'y': expected 'float', got " + str(type(y)))
        if type(z) != float:
            raise TypeError("Argument 'z': expected 'float', got " + str(type(z)))
        if type(radius) != float:
            raise TypeError("Argument 'radius': expected 'float', got " + str(type(radius)))
        if type(thickness) != float:
            raise TypeError("Argument 'thickness': expected 'float', got " + str(type(thickness)))
        if not isinstance(space, Space):
            raise TypeError("Argument 'space' is not an instance of class 'Space'")
        A = Point(space, x - 0.96 * radius, y - 0.636 * radius, z - thickness / 2)
        B = Point(space, x - 0.636 * radius, y - 0.96 * radius, z - thickness / 2)
        C = Point(space, x, y - 0.328 * radius, z - thickness / 2)
        E = Point(space, x + 0.96 * radius, y - 0.636 * radius, z - thickness / 2)
        D = Point(space, x + 0.636 * radius, y - 0.96 * radius, z - thickness / 2)
        F = Point(space, x + 0.328 * radius, y, z - thickness / 2)
        G = Point(space, x + 0.96 * radius, y + 0.636 * radius, z - thickness / 2)
        H = Point(space, x + 0.636 * radius, y + 0.96 * radius, z - thickness / 2)
        I = Point(space, x, y + 0.328 * radius, z - thickness / 2)
        K = Point(space, x - 0.96 * radius, y + 0.636 * radius, z - thickness / 2)
        J = Point(space, x - 0.636 * radius, y + 0.96 * radius, z - thickness / 2)
        L = Point(space, x - 0.328 * radius, y, z - thickness / 2)
        P1 = Polygon(space, [A, B, C, D, E, F, G, H, I, J, K, L], locate=False)
        P1.phantomPoint = Point(space, x, y, z - 2 * thickness)
        if lowConfig:
            Mesh.__init__(self, space, [P1])
        else:
            A2 = Point(space, x - 0.96 * radius, y - 0.636 * radius, z + thickness / 2)
            B2 = Point(space, x - 0.636 * radius, y - 0.96 * radius, z + thickness / 2)
            C2 = Point(space, x, y - 0.328 * radius, z + thickness / 2)
            E2 = Point(space, x + 0.96 * radius, y - 0.636 * radius, z + thickness / 2)
            D2 = Point(space, x + 0.636 * radius, y - 0.96 * radius, z + thickness / 2)
            F2 = Point(space, x + 0.328 * radius, y, z + thickness / 2)
            G2 = Point(space, x + 0.96 * radius, y + 0.636 * radius, z + thickness / 2)
            H2 = Point(space, x + 0.636 * radius, y + 0.96 * radius, z + thickness / 2)
            I2 = Point(space, x, y + 0.328 * radius, z + thickness / 2)
            K2 = Point(space, x - 0.96 * radius, y + 0.636 * radius, z + thickness / 2)
            J2 = Point(space, x - 0.636 * radius, y + 0.96 * radius, z + thickness / 2)
            L2 = Point(space, x - 0.328 * radius, y, z + thickness / 2)
            P2 = Polygon(space, [A2, B2, C2, D2, E2, F2, G2, H2, I2, J2, K2, L2], locate=False)
            P2.phantomPoint = Point(space, x, y, z + 2 * thickness)
            Mesh.__init__(self, space, [P1, P2])

    def __get_color(self):
        return (0, 200, 0)  # It's green

    color = property(__get_color)


class Circle(Mesh):
    """A mesh representing a circle

    Attributes:
        color (3-tuple): RGB color of the circle (read only)

    Note:
        Subclass from Mesh

    """

    def __init__(self, space, x, y, z, radius, thickness, lowConfig = False):
        if type(x) != float:
            raise TypeError("Argument 'x': expected 'float', got " + str(type(x)))
        if type(y) != float:
            raise TypeError("Argument 'y': expected 'float', got " + str(type(y)))
        if type(z) != float:
            raise TypeError("Argument 'z': expected 'float', got " + str(type(z)))
        if type(radius) != float:
            raise TypeError("Argument 'radius': expected 'float', got " + str(type(radius)))
        if type(thickness) != float:
            raise TypeError("Argument 'thickness': expected 'float', got " + str(type(thickness)))
        if not isinstance(space, Space):
            raise TypeError("Argument 'space' is not an instance of class 'Space'")
        P1 = []
        for i in range(10):
            P1.append(Point(space, x + radius * np.cos(np.pi * i / 5), y + radius * np.sin(np.pi * i / 5), z - thickness / 2))
        P1.append(P1[0])
        for i in range(11):
            P1.append(Point(space, x + 0.8 * radius * np.cos(np.pi * i / 5), y + 0.8 * radius * np.sin(np.pi * i / 5), z - thickness / 2))
        PP1 = Polygon(space, P1, locate=False)
        PP1.phantomPoint = Point(space, x, y, z - 2 * thickness)
        if lowConfig:
            Mesh.__init__(self, space, [PP1])
        else:
            P2 = []
            for i in range(10):
                P2.append(Point(space, x + radius * np.cos(np.pi * i / 5), y + radius * np.sin(np.pi * i / 5), z + thickness / 2))
            P2.append(P2[0])
            for i in range(11):
                P2.append(Point(space, x + 0.8 * radius * np.cos(np.pi * i / 5), y + 0.8 * radius * np.sin(np.pi * i / 5), z + thickness / 2))
            PP2 = Polygon(space, P2, locate=False)
            PP2.phantomPoint = Point(space, x, y, z + 2 * thickness)
            Mesh.__init__(self, space, [PP1, PP2])

    def __get_color(self):
        return (200, 0, 0)  # It's red

    color = property(__get_color)


class BigCircle(Mesh):
    """A big circle that circles around the grid
    """

    def __init__(self, space, radius, thickness, width):
        if type(radius) != float:
            raise TypeError("Argument 'radius': expected 'float', got " + str(type(radius)))
        if type(thickness) != float:
            raise TypeError("Argument 'thickness': expected 'float', got " + str(type(thickness)))
        if type(width) != float:
            raise TypeError("Argument 'width': expected 'float', got " + str(type(width)))
        if not isinstance(space, Space):
            raise TypeError("Argument 'space' is not an instance of class 'Space'")
        points1 = []
        points2 = []
        polygons = []
        n = 24
        for k in range(n):
            points1.append(Point(space, radius * np.cos(2 * np.pi * k / n), radius * np.sin(2*np.pi * k / n), -thickness / 2))
            points2.append(Point(space, radius * np.cos(2*np.pi * k / n), radius * np.sin(2*np.pi * k / n), +thickness / 2))
        for k in range(n):
            points1.append(Point(space, (radius - width) * np.cos(2*np.pi * k / n), (radius - width) * np.sin(2*np.pi * k / n), -thickness / 2))
            points2.append(Point(space, (radius - width) * np.cos(2*np.pi * k / n), (radius - width) * np.sin(2*np.pi * k / n), +thickness / 2))
        for k in range(n):
            polygons.append(Polygon(space, [points1[k], points1[(k + 1) % n], points1[n + (k + 1) % n], points1[n + k]], locate=False, normal = (0,0,-1)))
            polygons.append(Polygon(space, [points2[k], points2[(k + 1) % n], points2[n + (k + 1) % n], points2[n + k]], locate=False, normal = (0,0,1)))
            polygons.append(Polygon(space, [points1[k], points1[(k + 1) % n], points2[(k + 1) % n], points2[k]], locate=False, normal = (np.cos((k + 0.5)*2*np.pi/n),np.sin((k + 0.5)*2*np.pi/n),0)))
            polygons.append(Polygon(space, [points1[n + k], points1[n + (k + 1) % n], points2[n + (k + 1) % n], points2[n + k]], locate=False, normal = (-np.cos((k + 0.5)*2*np.pi/n),-np.sin((k + 0.5)*2*np.pi/n),0)))
        Mesh.__init__(self, space, polygons)
        self.change_speed()

    def change_speed(self):
        self.__wx = uniform(-0.02, 0.02)
        self.__wy = uniform(-0.02, 0.02)
        self.__wz = uniform(-0.02, 0.02)

    def step(self):
        ax, ay, az = self.angles
        self.angles = (ax + self.__wx, ay + self.__wy, az + self.__wz)

    def __get_color(self):
        return (150, 150, 255)

    color = property(__get_color)





