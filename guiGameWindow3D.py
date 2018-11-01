#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Class GameWindow3D, handling the displaying properties of the 3D grid and its state, and also handling the interaction
between the user and the grid (cell selection and grid rotation)
"""

import numpy as np

from guiDrawer import Drawer
from perspectiveprojection import Point, Space, Polygon, Mesh


class GameWindow3D:
    """A window managed with pygame. Is a thread
    
    Attributes:
        screen (pygame.Surface): the pygame screen
        testMessage (str): This string is displayed in the bottom left corner (read/write)
        
    """
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
        self.__heightSeparation = 22 / self.__gridSize  # Distance between each plane (real 3D distance)

        self.__stateMatrix = np.zeros([self.__gridSize, self.__gridSize, self.__gridSize])  # Matrix containing
        # the states of each cell (0 = empty, 1 = player1, 2 = opponent)

        self.__selectedCell = (-1, -1, -1)  # Coordinates of the selected cell ([-1,-1,-1] if no cell is selected)

        # Space which will contain all the points and polygons defining the grid
        self.__space = Space()  

        # Creating the cells
        self.__cells = [[[None for k in range(self.__gridSize)] for j in range(self.__gridSize)] for i in
                           range(self.__gridSize)]
        
        self.__cellSize = gridWidth / gridSize  # Width of a cell of the grid (real 3D width)
        
        for i in range(self.__gridSize):
            for j in range(self.__gridSize):
                for k in range(self.__gridSize):
                    xp = -self.__gridWidth / 2 + i * self.__cellSize
                    yp = -self.__gridWidth / 2 + j * self.__cellSize
                    zp = (-k + (self.__gridSize - 1) / 2) * self.__heightSeparation
                    self.__cells[i][j][k] = Cell(self.__space, xp, yp, zp, self.__cellSize, self.__heightSeparation/10, (i,j,k))

        """
        # Script to create a polygon defining a Circle (which will be drawn in the grid during the game)
        circle = []
        for i in range(10):
            circle.append(Point(self.__space, self.__cellSize / 2.5 * np.cos(2 * np.pi * i / 10),
                                self.__cellSize / 2.5 * np.sin(2 * np.pi * i / 10),
                                0))
        self._circlePolygon = Polygon(self.__space, circle, name="circle", locate=False)
        """
        
        # Set the view in a confortable angle and update the space instance
        self.__space.angles = (1,0,0.85)

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
            ax += speed
        elif direction == "down":
            ax -= speed
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
                cellPos = detectedPolygon.mesh.cellId
        self.__selectedCell = cellPos

    # ================ DRAWING METHODS ======================================

    def draw_grid(self):
        """Draw all the cells of the morpion, then draw the state of the  th"""

        self.__drawer.erase()
        for poly in reversed(self.__space.polygons):
            if isinstance(poly.mesh, Cell):
                i,j,k = poly.mesh.cellId
                self.__drawer.draw_cell(poly, 1 if (i, j, k) == self.__selectedCell else poly.mesh.color)
            elif isinstance(poly.mesh, Cross):
                self.__drawer.draw_cross(poly)
            elif isinstance(poly.mesh, Circle):
                self.__drawer.draw_circle(poly)
                """if self.__stateMatrix[i, j, k] != 0:
                    translation = (-self.__gridWidth / 2 + (i + 1 / 2) * self.__cellSize,
                                   -self.__gridWidth / 2 + (j + 1 / 2) * self.__cellSize,
                                   (-k + (self.__gridSize - 1) / 2) * self.__heightSeparation)
                    if self.__stateMatrix[i, j, k] == 1:
                        self.__drawer.draw_state(self._circlePolygon, translation, 1)
                    elif self.__stateMatrix[i, j, k] == 2:
                        self.__drawer.draw_state(self.__crossPolygon, translation, 2)"""
        if self.__selectedCell != (-1, -1, -1):
            i, j, k = self.__selectedCell
            self.__drawer.highlight_cell(self.__cells[i][j][k])

    def update_screen(self):
        self.draw_grid()

    # ============== METHODS RELATED TO INTERACTION WITH GAME ENGINE =============

    def highlight_winning_cell(self,cellId):
        """Change the color of the winning cells"""
        if type(cellId) != tuple:
            raise TypeError("Argument 'cellId': expected 'tuple', got " + str(type(cellId)))
        if len(cellId) != 3:
            raise ValueError("Tuple 'cellId' should have 3 elements, but has " + str(len(cellId)))
        if type(cellId[0]) != int or type(cellId[1]) != int or type(cellId[2]) != int:
            raise TypeError("Argument 'cellId' should be a tuple of integers")
        i,j,k = cellId
        self.__cells[i][j][k].color = 2
        self.__parentWindow.update_screen()

    def highlight_played_cell(self,cellId):
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
                    c.color = 0
        i,j,k = cellId
        self.__cells[i][j][k].color = 3
        self.__parentWindow.update_screen()

    def __get_state_matrix(self):
        return self.__stateMatrix

    def __set_state_matrix(self, newStateMatrix):
        for i in range(self.__gridSize):
            for j in range(self.__gridSize):
                for k in range(self.__gridSize):
                    if newStateMatrix[i][j][k] != self.__stateMatrix[i][j][k]:
                        xp = -self.__gridWidth / 2 + (i + 0.5) * self.__cellSize
                        yp = -self.__gridWidth / 2 + (j + 0.5) * self.__cellSize
                        zp = (-k + (self.__gridSize - 1) / 2) * self.__heightSeparation
                        if newStateMatrix[i][j][k] == 1:
                            Circle(self.__space, xp, yp, zp, 0.45 * self.__cellSize, self.__heightSeparation/10)
                        elif newStateMatrix[i][j][k] == 2:
                            Cross(self.__space, xp, yp, zp, 0.45 * self.__cellSize, self.__heightSeparation/10)
                        self.__space.update()
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



class Cell(Mesh):
    """A mesh (a rectangular cuboid) representing a cell
    
    Attributes:
        cellId (3-tuple): an id giving the position of the cell with in-game coordinates (read only)
        color (int): the color the cell should be drawn (read/write)
        
    Note:
        Subclass from Mesh
        
    """
    def __init__(self, space, x, y, z, width, thickness, cellId):
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
        A = Point(space, x, y, z - thickness/2)
        B = Point(space, x + width, y, z - thickness/2)
        C = Point(space, x + width, y + width, z - thickness/2)
        D = Point(space, x, y + width, z - thickness/2)
        E = Point(space, x, y, z + thickness/2)
        F = Point(space, x + width, y, z + thickness/2)
        G = Point(space, x + width, y + width, z + thickness/2)
        H = Point(space, x, y + width, z + thickness/2)
        P1 = Polygon(space, [A,B,C,D])
        P2 = Polygon(space, [B,C,G,F])
        P3 = Polygon(space, [C,D,H,G])
        P4 = Polygon(space, [H,E,A,D])
        P5 = Polygon(space, [F,E,A,B])
        P6 = Polygon(space, [E,F,G,H])
        Mesh.__init__(self, space, [P1, P2, P3, P4, P5, P6])
        self.__cellId = cellId
        self.__color = 0
    
  
    def __get_cell_id(self):
        return self.__cellId
    cellId = property(__get_cell_id)
    
    def __get_color(self):
        return self.__color
    def __set_color(self, c):
        self.__color = c
    color = property(__get_color, __set_color)
    
    
    

class Cross(Mesh):
    """A mesh representing a cross
    
    Attributes:
        cellId (3-tuple): an id giving the position of the cell with in-game coordinates (read only)
        color (int): the color the cell should be drawn (read/write)
        
    Note:
        Subclass from Mesh
        
    """
    def __init__(self, space, x, y, z, radius, thickness):
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
        A = Point(space, x - 0.96 * radius, y - 0.636 * radius, z - thickness/2)
        B = Point(space, x - 0.636 * radius, y - 0.96 * radius, z - thickness/2)
        C = Point(space, x, y - 0.328 * radius, z - thickness/2)
        E = Point(space, x + 0.96 * radius, y - 0.636 * radius, z - thickness/2)
        D = Point(space, x + 0.636 * radius, y - 0.96 * radius, z - thickness/2)
        F = Point(space, x + 0.328 * radius, y, z - thickness/2)
        G = Point(space, x + 0.96 * radius, y + 0.636 * radius, z - thickness/2)
        H = Point(space, x + 0.636 * radius, y + 0.96 * radius, z - thickness/2)
        I = Point(space, x, y + 0.328 * radius, z - thickness/2)
        K = Point(space, x - 0.96 * radius, y + 0.636 * radius, z - thickness/2)
        J = Point(space, x - 0.636 * radius, y + 0.96 * radius, z - thickness/2)
        L = Point(space, x - 0.328 * radius, y, z - thickness/2)
        P1 = Polygon(space, [A,B,C,D,E,F,G,H,I,J,K,L], locate = False)
        P1.phantomPoint = Point(space, x, y, z - 2 * thickness)
        A2 = Point(space, x - 0.96 * radius, y - 0.636 * radius, z + thickness/2)
        B2 = Point(space, x - 0.636 * radius, y - 0.96 * radius, z + thickness/2)
        C2 = Point(space, x, y - 0.328 * radius, z + thickness/2)
        E2 = Point(space, x + 0.96 * radius, y - 0.636 * radius, z + thickness/2)
        D2 = Point(space, x + 0.636 * radius, y - 0.96 * radius, z + thickness/2)
        F2 = Point(space, x + 0.328 * radius, y, z + thickness/2)
        G2 = Point(space, x + 0.96 * radius, y + 0.636 * radius, z + thickness/2)
        H2 = Point(space, x + 0.636 * radius, y + 0.96 * radius, z + thickness/2)
        I2 = Point(space, x, y + 0.328 * radius, z + thickness/2)
        K2 = Point(space, x - 0.96 * radius, y + 0.636 * radius, z + thickness/2)
        J2 = Point(space, x - 0.636 * radius, y + 0.96 * radius, z + thickness/2)
        L2 = Point(space, x - 0.328 * radius, y, z + thickness/2)
        P2 = Polygon(space, [A2,B2,C2,D2,E2,F2,G2,H2,I2,J2,K2,L2], locate = False)
        P2.phantomPoint = Point(space, x, y, z + 2 * thickness)
        Mesh.__init__(self, space, [P1, P2])
    
    
    
class Circle(Mesh):
    """A mesh representing a circle
    
    Attributes:
        cellId (3-tuple): an id giving the position of the cell with in-game coordinates (read only)
        color (int): the color the cell should be drawn (read/write)
        
    Note:
        Subclass from Mesh
        
    """
    def __init__(self, space, x, y, z, radius, thickness):
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
        P2 = []
        for i in range(10):
            P1.append(Point(space, x + radius * np.cos(np.pi * i / 5), y + radius * np.sin(np.pi * i / 5), z - thickness/2))
            P2.append(Point(space, x + radius * np.cos(np.pi * i / 5), y + radius * np.sin(np.pi * i / 5), z + thickness/2))
        P1.append(P1[0])
        P2.append(P2[0])
        for i in range(11):
            P1.append(Point(space, x + 0.8 * radius * np.cos(np.pi * i / 5), y + 0.9 * radius * np.sin(np.pi * i / 5), z - thickness/2))
            P2.append(Point(space, x + 0.8 * radius * np.cos(np.pi * i / 5), y + 0.9 * radius * np.sin(np.pi * i / 5), z + thickness/2))
        PP1 = Polygon(space, P1, locate = False)
        PP2 = Polygon(space, P2, locate = False)
        PP1.phantomPoint = Point(space, x, y, z - 2 * thickness)
        PP2.phantomPoint = Point(space, x, y, z + 2 * thickness)
        Mesh.__init__(self, space, [PP1, PP2])
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    