#import numpy as np
from guiDrawer import Drawer
from perspectiveprojection import *


class GameWindow3D:

    def __init__(self, parentWindow, gridWidth, gridSize):
        """Take as input the size of the grid and the position of the top left corner of the grid"""
        self.parentWindow = parentWindow
        self.screen = parentWindow.get_screen()
        self.drawer = Drawer(self.screen)
        
        self._gridSize = gridSize  # Size of the grid (default = 3)
        self._gridWidth = gridWidth  # gridWidth  # Overall width of the grid (real 3d width)
        self._cellSize = gridWidth / gridSize
        self._heightSeparation = 22 / self.gridSize  # Distance between each plane in the screen

        self._stateMatrix = np.zeros([self.gridSize, self.gridSize, self.gridSize])
        self._coloringMatrix = np.zeros([self.gridSize, self.gridSize, self.gridSize])

        self.selectedCell = [-1, -1, -1]  # Coordinates of the selected cell ([-1,-1,-1] if no cell is selected)

        self._space = Space()        
        
        self._points = [[[ None for k in range(self._gridSize+1)]for j in range(self._gridSize+1)] for i in range(self._gridSize+1)]
        
        for i in range(self._gridSize+1):
            for j in range(self._gridSize+1):
                for k in range(self._gridSize+1):
                    xp = -self.gridWidth / 2 + i * self._cellSize
                    yp = -self.gridWidth / 2 + j * self._cellSize
                    zp = (k - (self.gridSize - 1) // 2) * self._heightSeparation
                    self.points[i][j][k] = Point(self._space, xp, yp, zp)
        
        self._polygons = [[[ None for k in range(self.gridSize)]for j in range(self.gridSize)] for i in range(self.gridSize)]
        
        for i in range(self._gridSize):
            for j in range(self._gridSize):
                for k in range(self._gridSize):
                    P1 = self._points[i][j][k]
                    P2 = self._points[i+1][j][k]
                    P3 = self._points[i][j+1][k]
                    P4 = self._points[i+1][j+1][k]
                    self._polygons[i][j][k] = Polygon(self._space, [P1,P2,P4,P3], name = 'cell' + str(i) + str(j) + str(k))
        
        self.statePoints1 = []
        self.statePoints2 = []

        self.statePoints1.append(Point(self.space, 0, 0, 0))
        self.statePoints1.append(Point(self.space, -self._cellSize / 2.5, -self._cellSize / 2.5, 0))
        self.statePoints1.append(Point(self.space, self._cellSize / 2.5, self._cellSize / 2.5, 0))
        self.statePoints1.append(Point(self.space, 0, 0, 0))
        self.statePoints1.append(Point(self.space, -self._cellSize / 2.5, self._cellSize / 2.5, 0))
        self.statePoints1.append(Point(self.space, self._cellSize / 2.5, -self._cellSize / 2.5, 0))
        self.statePolygon1 = Polygon(self.space, self.statePoints1, "cross", False)

        for i in range(10):
            self.statePoints2.append(Point(self.space, self._cellSize / 2.5 * np.cos(2 * np.pi * i / 10),
                                           self._cellSize / 2.5 * np.sin(2 * np.pi * i / 10),
                                           0))

        self.statePolygon2 = Polygon(self.space, self.statePoints2, "circle", False)
        self.update_screen()

    # ================ EVENT MANAGEMENT METHODS =============================

    def move(self, direction, speed):
        if direction == "left":
            self.space.angles = [self.space.angles[0], self.space.angles[1], self.space.angles[2] + speed]
            self.parentWindow.update_screen()
        elif direction == "right":
            self.space.angles = [self.space.angles[0], self.space.angles[1], self.space.angles[2] - speed]
            self.parentWindow.update_screen()
        elif direction == "up":
            self.space.angles = [self.space.angles[0] + speed, self.space.angles[1], self.space.angles[2]]
            self.parentWindow.update_screen()
        elif direction == "down":
            self.space.angles = [self.space.angles[0] + speed, self.space.angles[1], self.space.angles[2]]
            self.parentWindow.update_screen()

    def get_played_cell(self):
        """Returns the cell coordinates and reinitialize selectedCell to [-1,-1,-1]"""
        cell = self.selectedCell.copy()
        self.selectedCell = [-1, -1, -1]
        self.parentWindow.update_screen()
        return cell

    def detect_cell_pos(self, mousePos):
        """Changes the cell coordinates corresponding to the mouse position ([-1,-1] = out of the grid)"""
        cellPos = [-1, -1, -1]
        ((xmin, ymin), (xmax, ymax)) = self.space.xyBounds
        if (xmin <= mousePos[0] <= xmax) and (ymin < mousePos[1] < ymax) :
            detectedPolygon = self.space.locate_polygon(mousePos[0], mousePos[1])
            if detectedPolygon != None:
                cellPos = [int(detectedPolygon.name[0]), int(detectedPolygon.name[1]), int(detectedPolygon.name[2])]
            self.selectedCell = cellPos

            self.parentWindow.textMessage = str(self.selectedCell[0]) + str(self.selectedCell[1]) + str(
                self.selectedCell[2]) \
                                            + " MinDepth=" + str(
                int(self.polygons[cellPos[0]][cellPos[1]][cellPos[2]].depth[0])) \
                                            + " AvgDepth=" + str(
                int(self.polygons[cellPos[0]][cellPos[1]][cellPos[2]].depth[1])) \
                                            + " MaxDepth=" + str(
                int(self.polygons[cellPos[0]][cellPos[1]][cellPos[2]].depth[2]))

    # ================ DRAWING METHODS ======================================

    def draw_grid(self):
        """Draw all the edges of the morpion grid taking into account the grid position and its size"""

        self.drawer.erase()
        for k in range(self.gridSize - 1, -1, -1):
            for i in range(self.gridSize):
                for j in range(self.gridSize):
                    if self.selectedCell == [i, j, k]:
                        self.drawer.drawCell(self.polygons[i][j][k],1) # 1 = Selected cell
                    else :
                        self.drawer.drawCell(self.polygons[i][j][k], 1)  # 0 = Unselected cell
                    if self.stateMatrix[i, j, k] != 0:
                        translation = [-self.gridWidth / 2 + (i + 1 / 2) * self._cellSize,
                                       -self.gridWidth / 2 + (j + 1 / 2) * self._cellSize,
                                       (k - int((self.gridSize - 1) / 2)) * self.heightSeparation]
                        if self.stateMatrix[i, j, k] == 1:
                            self.drawer.drawState(self.statePolygon1,translation,1)
                        elif self.stateMatrix[i, j, k] == 2:
                            self.drawer.drawState(self.statePolygon2, translation, 2)
        if self.selectedCell != [-1, -1, -1]:
            self.drawer.highlightCell(self.polygons[self.selectedCell[0]][self.selectedCell[1]][self.selectedCell[2]])

    def update_screen(self):
        self.draw_grid()
        # self.draw_selected_cell()
        # self.draw_current_state()

    # ============== METHODS RELATED TO DISPLAYING PROPERTIES =============

    def _get_grid_width(self):
        return self._gridWidth

    def _set_grid_width(self, newGridWidth):
        self._gridWidth = newGridWidth

    def _get_grid_size(self):
        return self._gridSize

    def _set_grid_size(self, newgridSize):
        self._gridSize = list(newgridSize)

    def _get_state_matrix(self):
        return self._stateMatrix

    def _set_state_matrix(self, newStateMatrix):
        self._stateMatrix = np.array(newStateMatrix)
        self._stateMatrix = self._stateMatrix.astype(int)
        self.parentWindow.update_screen()

    gridWidth = property(_get_grid_width, _set_grid_width)
    gridSize = property(_get_grid_size, _set_grid_size)
    stateMatrix = property(_get_state_matrix, _set_state_matrix)
