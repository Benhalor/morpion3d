import numpy as np
from guiDrawer import Drawer


class GameWindow:

    def __init__(self, parentWindow, gridWidth, gridSize):
        """Take as input the size of the grid and the position of the top left corner of the grid"""
        self._parentWindow = parentWindow
        self._drawer = Drawer(parentWindow.screen)

        self._gridSize = gridSize  # Size of the grid (default = 3)
        self._gridWidth = gridWidth  # gridWidth  # Overall width of the grid (real 3d width)
        self._cellSize = gridWidth / gridSize

        self.update_screen()

    # ================ EVENT MANAGEMENT METHODS =============================

    def detect_cell_pos(self, mousePos):
        """Changes the cell coordinates corresponding to the mouse position ([-1,-1,-1] = out of the grid)"""
        pass

    # ================ DRAWING METHODS ======================================

    def draw_grid(self):
        """Draw all the edges of the morpion grid taking into account the grid position and its size"""
        pass

    def update_screen(self):
        self.draw_grid()

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
        cell = self._selectedCell.copy()
        self._selectedCell = (-1, -1, -1)
        self._parentWindow.update_screen()
        return cell

    gridWidth = property(_get_grid_width)
    gridSize = property(_get_grid_size)
    stateMatrix = property(_get_state_matrix, _set_state_matrix)
    playedCell = property(_get_played_cell)
