import numpy as np
from guiDrawer import Drawer
from perspectiveprojection import *


class GameWindow3D:

    def __init__(self, parentWindow, gridWidth, gridSize):
        """Take as input the size of the grid and the position of the top left corner of the grid"""
        self._parentWindow = parentWindow
        self._drawer = Drawer(parentWindow.screen)
        
        self._gridSize = gridSize  # Size of the grid (default = 3)
        self._gridWidth = gridWidth  # gridWidth  # Overall width of the grid (real 3d width)
        self._cellSize = gridWidth / gridSize
        self._heightSeparation = 22 / self.gridSize  # Distance between each plane in the screen

        self._stateMatrix = np.zeros([self._gridSize, self._gridSize, self._gridSize])
        self._coloringMatrix = np.zeros([self._gridSize, self._gridSize, self._gridSize])

        self._selectedCell = (-1, -1, -1)  # Coordinates of the selected cell ([-1,-1,-1] if no cell is selected)

        self._space = Space()
        ax, ay, az = self._space.angles
        self._space.angles = (ax - 0.25, ay + 0.25, az + 0.05)
        
        # Cells points
        self._points = [[[ None for k in range(self._gridSize+1)]for j in range(self._gridSize+1)] for i in range(self._gridSize+1)]
        for i in range(self._gridSize+1):
            for j in range(self._gridSize+1):
                for k in range(self._gridSize):
                    xp = -self.gridWidth / 2 + i * self._cellSize
                    yp = -self.gridWidth / 2 + j * self._cellSize
                    zp = (-k + (self.gridSize - 1) // 2) * self._heightSeparation
                    self._points[i][j][k] = Point(self._space, xp, yp, zp)
        
        # Cells polygons
        self._polygons = [[[ None for k in range(self.gridSize)]for j in range(self.gridSize)] for i in range(self.gridSize)]
        for i in range(self._gridSize):
            for j in range(self._gridSize):
                for k in range(self._gridSize):
                    P1 = self._points[i][j][k]
                    P2 = self._points[i+1][j][k]
                    P3 = self._points[i][j+1][k]
                    P4 = self._points[i+1][j+1][k]
                    self._polygons[i][j][k] = Polygon(self._space, [P1,P2,P4,P3], name = 'cell' + str(i) + str(j) + str(k))
        
        # Cross
        C1 = Point(self._space, 0, 0, 0)
        C2 = Point(self._space, -self._cellSize / 2.5, -self._cellSize / 2.5, 0)
        C3 = Point(self._space, self._cellSize / 2.5, self._cellSize / 2.5, 0)
        C4 = Point(self._space, 0, 0, 0)
        C5 = Point(self._space, -self._cellSize / 2.5, self._cellSize / 2.5, 0)
        C6 = Point(self._space, self._cellSize / 2.5, -self._cellSize / 2.5, 0)
        self._crossPolygon = Polygon(self._space, [C1, C2, C3, C4, C5, C6], name = "cross", locate = False)
        
        
        circle = []
        for i in range(10):
            circle.append(Point(self._space, self._cellSize / 2.5 * np.cos(2 * np.pi * i / 10),
                                           self._cellSize / 2.5 * np.sin(2 * np.pi * i / 10),
                                           0))
        self._circlePolygon = Polygon(self._space, circle, name = "circle", locate = False)
        
        self.update_screen()

    # ================ EVENT MANAGEMENT METHODS =============================

    def move(self, direction, speed):
        ax, ay, az = self._space.angles
        if direction == "left":
            az += speed
        elif direction == "right":
            az -= speed
        elif direction == "up":
            ax += speed
        elif direction == "down":
            ax -= speed
        self._space.angles = (ax, ay, az)
        self._parentWindow.update_screen()

    def detect_cell_pos(self, mousePos):
        """Changes the cell coordinates corresponding to the mouse position ([-1,-1,-1] = out of the grid)"""
        cellPos = (-1, -1, -1)
        ((xmin, ymin), (xmax, ymax)) = self._space.xyBounds
        if (xmin <= mousePos[0] <= xmax) and (ymin <= mousePos[1] <= ymax) :
            detectedPolygon = self._space.locate_polygon(mousePos[0], mousePos[1])
            if detectedPolygon is not None:
                cellPos = (int(detectedPolygon.name[4]), int(detectedPolygon.name[5]), int(detectedPolygon.name[6]))
            self._selectedCell = cellPos

            self._parentWindow.textMessage = str(self._selectedCell[0]) + str(self._selectedCell[1]) + str(self._selectedCell[2])

    # ================ DRAWING METHODS ======================================

    def draw_grid(self):
        """Draw all the edges of the morpion grid taking into account the grid position and its size"""

        self._drawer.erase()
        for poly in reversed(self._space.polygons):
            name = poly.name
            if len(name) >= 4 and name[:4] == "cell":
                i = int(name[4])
                j = int(name[5])
                k = int(name[6])
                self._drawer.draw_cell(poly, 1 if (i,j,k) == self._selectedCell else 0)
                if self._stateMatrix[i,j,k] != 0:
                    translation = (-self.gridWidth / 2 + (i + 1 / 2) * self._cellSize,
                                       -self.gridWidth / 2 + (j + 1 / 2) * self._cellSize,
                                       (k - (self.gridSize - 1) // 2) * self._heightSeparation)
                    if self._stateMatrix[i,j,k] == 1:
                        self._drawer.draw_state(self._circlePolygon, translation, 1)
                    elif self._stateMatrix[i,j,k] == 2:
                        self._drawer.draw_state(self._crossPolygon, translation, 2)
        if self._selectedCell != (-1,-1,-1):
            i,j,k = self._selectedCell
            self._drawer.highlight_cell(self._polygons[i][j][k])
                
    def update_screen(self):
        self.draw_grid()
        # self.draw_selected_cell()
        # self.draw_current_state()

    # ============== METHODS RELATED TO DISPLAYING PROPERTIES =============

    def _get_grid_width(self):
        return self._gridWidth

    def _get_grid_size(self):
        return self._gridSize

    def _get_state_matrix(self):
        return self._stateMatrix

    def _set_state_matrix(self, newStateMatrix):
        self._stateMatrix = np.array(newStateMatrix)
        self._stateMatrix = self._stateMatrix.astype(int)
        self._parentWindow.update_screen()
        
    def _get_played_cell(self):
        """Returns the cell coordinates and reinitialize selectedCell to [-1,-1,-1]"""
        cell = self._selectedCell
        self._selectedCell = (-1, -1, -1)
        self._parentWindow.update_screen()
        return cell

    gridWidth = property(_get_grid_width)
    gridSize = property(_get_grid_size)
    stateMatrix = property(_get_state_matrix, _set_state_matrix)
    playedCell = property(_get_played_cell)
