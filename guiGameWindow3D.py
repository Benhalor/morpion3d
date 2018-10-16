import pygame
import numpy as np

from threading import Thread

from pygame.locals import *


class GameWindow3D:

    def __init__(self, parentWindow, gridWidth, gridPos, dim):
        """Take as input the size of the grid and the position of the top left corner of the grid"""
        self.parentWindow = parentWindow
        self.screen = parentWindow.get_screen()

        self.color1 = [255, 0, 0]
        self.color2 = [0, 255, 0]
        self.colorHighlight = [255,255,0]

        self._gridWidth = 200  # gridWidth  # Overall width of the grid (real 3d width)
        self._gridPos = np.array(
            gridPos)  # Position in the screen of the top left corner of the grid (highest point in the
        # screen in isometric view)
        self._gridDim = dim  # Dimension of the grid (default = 3)
        self.heightSeparation = 100  # Distance between each plane in the screen

        self._viewAngle = np.pi / 4
        self._leftAngle = np.pi / 12
        self._rightAngle = np.pi / 12
        self._leftWidth = 0.82
        self._rightWidth = 0.82
        self._leftVector = self._leftWidth * np.array(
            [np.cos(np.pi - self._leftAngle), -np.sin(np.pi - self._leftAngle)])
        self._rightVector = self._rightWidth * np.array([np.cos(self._rightAngle), -np.sin(self._rightAngle)])

        self._basisMatrix = (self.gridWidth/self.gridDim)*np.array([[self._rightVector[0],self._leftVector[0]],
                                                                    [self._rightVector[1],self._leftVector[1]]])
        self._invMatrix = np.linalg.inv(self._basisMatrix)
        self._stateMatrix = np.zeros([self.gridDim,self.gridDim,self.gridDim])

        self._cellSize = 0
        self._cellPos = 0
        self.compute_grid_properties()

        self.selectedCell = [-1, -1, -1]  # Coordinates of the selected cell ([-1,-1,-1] if no cell is selected)
        self.update_screen()

        boolContinue = True

    # ================ EVENT MANAGEMENT METHODS =============================

    def get_played_cell(self):
        # ============TO DO=====================
        cell = self.selectedCell.copy()
        self.selectedCell = [-1, -1, -1]
        self.parentWindow.update_screen()
        return cell

    def detect_cell_pos(self, mousePos):
        """Returns the cell coordinates corresponding to the mouse position ([-1,-1] = out of the grid)"""
        # ============TO DO=====================
        cellPos = [-1, -1, -1]
        for k in range(self.gridDim):
            relPos = np.array(mousePos)-(self.gridPos+np.array([0, k])*self.heightSeparation)
            gridCoordinates = np.matmul(self._invMatrix,relPos)+3
            if self.gridDim > gridCoordinates[0] >= 0 and self.gridDim > gridCoordinates[1] >= 0:
                cellPos[0] = -int(np.floor(gridCoordinates[0]))+self.gridDim-1
                cellPos[1] = -int(np.floor(gridCoordinates[1]))+self.gridDim-1
                cellPos[2] = k
        self.selectedCell = cellPos

    # ================ DRAWING METHODS ======================================

    def draw_grid(self):
        """Draw all the edges of the morpion grid taking into account the grid position and its size"""
        gridColor = [255, 255, 255]
        self.screen.fill([10, 10, 70])  # Fill the screen (background color)
        for j in range(self.gridDim):  # For each plane of the grid
            gPos = self.gridPos + np.array([0, j * self.heightSeparation])
            for i in range(self.gridDim + 1):  # For each line in each plane
                pygame.draw.line(self.screen, gridColor, gPos - i * self._leftVector * self._cellSize,
                                 gPos - self._rightVector * self.gridWidth - i * self._leftVector * self._cellSize)
                pygame.draw.line(self.screen, gridColor, gPos - i * self._rightVector * self._cellSize,
                                 gPos - self._leftVector * self.gridWidth - i * self._rightVector * self._cellSize)

    def draw_current_state(self):
        """Draw the current state of the grid, (all the circles) taking into account an input state matrix (3x3)"""
        for i in range(np.size(self.stateMatrix, 0)):
            for j in range(np.size(self.stateMatrix, 1)):
                for k in range(np.size(self.stateMatrix, 2)):
                    if self.stateMatrix[i, j, k] != 0:
                        position = self._cellPos + (-j * self._leftVector - i * self._rightVector) * self._cellSize \
                                   + self.heightSeparation * k * np.array([0, 1])
                        position = position.astype(int)
                        if self.stateMatrix[i, j, k] == 1:
                            pygame.draw.circle(self.screen, self.color1, position, int(0.1 * self._cellSize))
                        elif self.stateMatrix[i, j, k] == 2:
                            pygame.draw.circle(self.screen, self.color2, position, int(0.1 * self._cellSize))

    def draw_selected_cell(self):
        """Highlight the selected cell"""
        if self.selectedCell != [-1, -1, -1]:
            selCellPos = self.gridPos + (-self.selectedCell[1] * self._leftVector - self.selectedCell[0] * self._rightVector) * self._cellSize \
                                   + self.heightSeparation * self.selectedCell[2] * np.array([0, 1])
            pygame.draw.lines(self.screen, self.colorHighlight, True, [selCellPos,
                                                                       selCellPos-self._leftVector*self._cellSize,
                                                                       selCellPos - (self._leftVector+self._rightVector) * self._cellSize,
                                                                       selCellPos - self._rightVector * self._cellSize],2)

    def update_screen(self):
        self.draw_grid()
        self.draw_current_state()
        self.draw_selected_cell()

    # ============== METHODS RELATED TO DISPLAYING PROPERTIES =============

    def compute_grid_properties(self):
        """Compute other grid properties depending on the parameters specified by the user"""
        self._cellSize = int(self.gridWidth / self.gridDim)  # Size of a cell depending on the grid width
        self._cellPos = (self.gridPos - (self._leftVector + self._rightVector)* self._cellSize / 2).astype(int)

    def update_perspective_properties(self):
        self._leftAngle = np.pi / 12
        self._rightAngle = np.pi / 12
        self._leftWidth = 0.82
        self._rightWidth = 0.82
        self._leftVector = self._leftWidth * np.array(
            [np.cos(np.pi - self._leftAngle), -np.sin(np.pi - self._leftAngle)])
        self._rightVector = self._rightWidth * np.array([np.cos(self._rightAngle), -np.sin(self._rightAngle)])
        self.parentWindow.update_screen()

    def _get_grid_width(self):
        return self._gridWidth

    def _set_grid_width(self, newGridWidth):
        self._gridWidth = newGridWidth
        self.compute_grid_properties()

    def _get_grid_pos(self):
        return self._gridPos

    def _set_grid_pos(self, newGridPos):
        self._gridPos = np.array(newGridPos)
        self.compute_grid_properties()

    def _get_grid_dim(self):
        return self._gridDim

    def _set_grid_dim(self, newGridDim):
        self._gridDim = list(newGridDim)
        self.compute_grid_properties()

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
