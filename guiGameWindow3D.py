import pygame

from guiDrawer import Drawer
from perspectiveprojection import *


class GameWindow3D:

    def __init__(self, parentWindow, gridWidth, gridPos, dim):
        """Take as input the size of the grid and the position of the top left corner of the grid"""
        self.parentWindow = parentWindow
        self.screen = parentWindow.get_screen()
        self.drawer = Drawer(self.screen)




        self._gridDim = dim  # Dimension of the grid (default = 3)
        self._gridWidth = gridWidth  # gridWidth  # Overall width of the grid (real 3d width)
        self._cellSize = self.gridWidth / self.gridDim
        self._gridPos = np.array(gridPos)  # Position in the screen of the top left corner of the grid (highest point in
        #  the screen in isometric view)

        self.heightSeparation = 22 / self.gridDim  # Distance between each plane in the screen

        self._stateMatrix = np.zeros([self.gridDim, self.gridDim, self.gridDim])
        self._coloringMatrix = np.zeros([self.gridDim, self.gridDim, self.gridDim])

        self.selectedCell = [-1, -1, -1]  # Coordinates of the selected cell ([-1,-1,-1] if no cell is selected)

        self.space = Space()
        axx, axy, axz = self.space.axes
        # print(self.space.axes)
        # self.space.axes = (axx,axy,(-axz[0],-axz[1],-axz[2]))

        self.points = []
        self.polygons = []

        self.statePoints1 = []
        self.statePoints2 = []

        for i in range(self.gridDim):
            self.points.append([])
            self.polygons.append([])
            for j in range(self.gridDim):
                self.points[i].append([])
                self.polygons[i].append([])
                for k in range(self.gridDim):
                    self.points[i][j].append([])

                    if i == 0 or j == 0:
                        self.points[i][j][k].append(Point(self.space, -self.gridWidth / 2 + i * self._cellSize,
                                                          -self.gridWidth / 2 + j * self._cellSize,
                                                          (k - int((self.gridDim - 1) / 2)) * self.heightSeparation))
                    else:
                        self.points[i][j][k].append(self.points[i - 1][j - 1][k][2])

                    if j == 0:
                        self.points[i][j][k].append(Point(self.space, -self.gridWidth / 2 + (i + 1) * self._cellSize,
                                                          -self.gridWidth / 2 + j * self._cellSize,
                                                          (k - int((self.gridDim - 1) / 2)) * self.heightSeparation))
                    else:
                        self.points[i][j][k].append(self.points[i][j - 1][k][2])

                    self.points[i][j][k].append(Point(self.space, -self.gridWidth / 2 + (i + 1) * self._cellSize,
                                                      -self.gridWidth / 2 + (j + 1) * self._cellSize,
                                                      (k - int((self.gridDim - 1) / 2)) * self.heightSeparation))

                    if i == 0:
                        self.points[i][j][k].append(Point(self.space, -self.gridWidth / 2 + i * self._cellSize,
                                                          -self.gridWidth / 2 + (j + 1) * self._cellSize,
                                                          (k - int((self.gridDim - 1) / 2)) * self.heightSeparation))
                    else:
                        self.points[i][j][k].append(self.points[i - 1][j][k][2])
                    self.polygons[i][j].append(
                        Polygon(self.space, [self.points[i][j][k][p] for p in range(4)], str(i) + str(j) + str(k)))

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
        for k in range(self.gridDim - 1, -1, -1):
            for i in range(self.gridDim):
                for j in range(self.gridDim):
                    if self.selectedCell == [i, j, k]:
                        self.drawer.drawCell(self.polygons[i][j][k],1) # 1 = Selected cell
                    else :
                        self.drawer.drawCell(self.polygons[i][j][k], 1)  # 0 = Unselected cell
                    if self.stateMatrix[i, j, k] != 0:
                        translation = [-self.gridWidth / 2 + (i + 1 / 2) * self._cellSize,
                                       -self.gridWidth / 2 + (j + 1 / 2) * self._cellSize,
                                       (k - int((self.gridDim - 1) / 2)) * self.heightSeparation]
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

    def _get_grid_pos(self):
        return self._gridPos

    def _set_grid_pos(self, newGridPos):
        self._gridPos = np.array(newGridPos)

    def _get_grid_dim(self):
        return self._gridDim

    def _set_grid_dim(self, newGridDim):
        self._gridDim = list(newGridDim)

    def _get_state_matrix(self):
        return self._stateMatrix

    def _set_state_matrix(self, newStateMatrix):
        self._stateMatrix = np.array(newStateMatrix)
        self._stateMatrix = self._stateMatrix.astype(int)
        self.parentWindow.update_screen()

    gridWidth = property(_get_grid_width, _set_grid_width)
    gridPos = property(_get_grid_pos, _set_grid_pos)
    gridDim = property(_get_grid_dim, _set_grid_dim)
    stateMatrix = property(_get_state_matrix, _set_state_matrix)
