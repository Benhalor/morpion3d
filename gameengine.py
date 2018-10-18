#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 10:09:31 2018

@author: armand
"""

class Player:
    
    def __init__(self, name):
        self._game = None
        self._name = name
        self._history = []
        
    def __str__(self):
        return self._name
        
    def _get_game(self):
        return self._game
    def _set_game(self, g):
        self._game = g
    game = property(_get_game, _set_game)
    
    def _get_name(self):
        return self._name
    name = property(_get_name)
    
    def _get_history(self):
        return self._history
    def clear_history(self):
        self._history = []
    history = property(_get_history)
    
    def play(self, c):
        """Player tries to play at c = (x,y,z)
        Exit codes:
            1: space is not free
            2: not player's turn
            3: valid play, games continue
            4: valid play, victory
            5: valid play, draw (grid full with no victory)"""
        if self.game:
            code = self._game.play_coordinates(c, self)
            return code
            

class HumanPlayer(Player):
    
    def __init__(self, game):
        Player.__init__(self, game)


class ComputerPlayer(Player):
    
    def __init__(self, game):
        Player.__init__(self, game)
    

class NetworkPlayer(Player):
    
    def __init__(self, game):
        Player.__init__(self, game)


class Grid:
    def __init__(self, size):
        self._size = size
        self._tokenFree = 0
        self._tokenPlayer1 = 1
        self._tokenPlayer2 = 2
        self._table = []
        self._gridCapacity = 0
        self._gridFilling = 0
        self._winningCoordinates = []
        self._rowsCodes = []
        self._rowsVect = dict()
        self._rowsCheck = dict()
        self._rowsPoint = dict()
        
    def __str__(self):
        return "Instance of grid object with size " + str(self._size)
        
    def _get_size(self):
        return self._size
    size = property(_get_size)
    
    def _get_table(self):
        return self._table
    table = property(_get_table)
    
    def _get_winningCoordinates(self):
        return self._winningCoordinates
    winningCoordinates = property(_get_winningCoordinates)
    
    def is_full(self):
        return self._gridCapacity == self._gridFilling
        
    def check_victory(self, playingPoint):
        """Checks if the given points is in a victorious row
        Updates self._winningCoordinates if True"""
        for code in self._rowsCodes:
            if self._rowsCheck[code](playingPoint):
                if self.check_row(self._rowsPoint[code](playingPoint), self._rowsVect[code]):
                    return True
        return False
    

class Grid2D(Grid):
    def __init__(self, size):
        Grid.__init__(self, size)
        self._table = [[self._tokenFree for y in range(self._size)] for x in range(self._size)]
        self._winningCoordinates = [(-1,-1) for k in range(self._size)]
        self._gridCapacity = self._size**2
        self._rowsCodes = ['h', 'v', 'd1', 'd2']
        self._rowsVect['h'] = (1,0)
        self._rowsPoint['h'] = lambda c: (0,c[1])
        self._rowsCheck['h'] = lambda c: True
        self._rowsVect['v'] = (0,1)
        self._rowsPoint['v'] = lambda c: (c[0],0)
        self._rowsCheck['v'] = lambda c: True
        self._rowsVect['d1'] = (1,1)
        self._rowsPoint['d1'] = lambda c: (0,0)
        self._rowsCheck['d1'] = lambda c: c[0] == c[1]
        self._rowsVect['d2'] = (1,-1)
        self._rowsPoint['d2'] = lambda c: (0,self._size-1)
        self._rowsCheck['d2'] = lambda c: c[0] + c[1] == self._size-1
        
    def __str__(self):
        return "2D grid instance with size " + str(self._size)
        
    def clear(self):
        """Clears the game grid"""
        for i in range(self._size):
            for j in range(self._size):
                self._table[i][j] = self._tokenFree
        self._winningCoordinates = [(-1,-1) for k in range(self._size)]
    
    def is_free(self, c):
        """Checks if the given coordinates c = (x,y) point to a free space"""
        x,y = c
        return self._table[x][y] == self._tokenFree
    
    def set_grid_element(self, c, player):
        """Set the point at the given coordinates c = (x,y) with the player token"""
        x = max(0, min(self._size - 1, c[0]))
        y = max(0, min(self._size - 1, c[1]))
        if player == 0:
            if self._table[x][y] != self._tokenFree:
                self._gridFilling -= 1
            self._table[x][y] = self._tokenFree
        elif player == 1:
            if self._table[x][y] == self._tokenFree:
                self._gridFilling += 1
            self._table[x][y] = self._tokenPlayer1
        elif player == 2:
            if self._table[x][y] == self._tokenFree:
                self._gridFilling += 1
            self._table[x][y] = self._tokenPlayer2

    
    def check_row(self, point, vector):
        """Returns True and updates _winningCoordinates if the given row is a winning one, False if not
        The row is specified by starting point + directional vector"""
        x,y = point
        vx, vy = vector
        t = self._table[x][y]
        for k in range(self._size):
            if self._table[x + k*vx][y + k*vy] != t:
                break
        else:
            self._winningCoordinates = [(x + k*vx, y + k*vy) for k in range(self._size)]
            return True
        return False
    

        
class Grid3D(Grid):
    def __init__(self, size):
        Grid.__init__(self, size)
        self._table = [[[self._tokenFree for z in range(self._size)] for y in range(self._size)] for x in range(self._size)]
        self._winningCoordinates = [(-1,-1,-1) for k in range(self._size)]
        self._gridCapacity = self._size**3
        self._rowsCodes = ['x', 'y', 'z', 'xy1', 'xy2', 'xz1', 'xz2', 'yz1', 'yz2', 'xyz1', 'xyz2', 'xyz3', 'xyz4']
        self._rowsVect['x'] = (1,0,0)
        self._rowsPoint['x'] = lambda c: (0,c[1],c[2])
        self._rowsCheck['x'] = lambda c: True
        self._rowsVect['y'] = (0,1,0)
        self._rowsPoint['y'] = lambda c: (c[0],0,c[2])
        self._rowsCheck['y'] = lambda c: True
        self._rowsVect['z'] = (0,0,1)
        self._rowsPoint['z'] = lambda c: (c[0],c[1],0)
        self._rowsCheck['z'] = lambda c: True
        self._rowsVect['xy1'] = (1,1,0)
        self._rowsPoint['xy1'] = lambda c: (0,0,c[2])
        self._rowsCheck['xy1'] = lambda c: c[0] == c[1]
        self._rowsVect['xy2'] = (1,-1,0)
        self._rowsPoint['xy2'] = lambda c: (0,self._size-1,c[2])
        self._rowsCheck['xy2'] = lambda c: c[0] + c[1] == self._size-1
        self._rowsVect['xz1'] = (1,0,1)
        self._rowsPoint['xz1'] = lambda c: (0,c[1],0)
        self._rowsCheck['xz1'] = lambda c: c[0] == c[2]
        self._rowsVect['xz2'] = (1,0,-1)
        self._rowsPoint['xz2'] = lambda c: (0,c[1],self._size-1)
        self._rowsCheck['xz2'] = lambda c: c[0] + c[2] == self._size-1
        self._rowsVect['yz1'] = (0,1,1)
        self._rowsPoint['yz1'] = lambda c: (c[0],0,0)
        self._rowsCheck['yz1'] = lambda c: c[2] == c[1]
        self._rowsVect['yz2'] = (0,1,-1)
        self._rowsPoint['yz2'] = lambda c: (c[0],0,self._size-1)
        self._rowsCheck['yz2'] = lambda c: c[2] + c[1] == self._size-1
        self._rowsVect['xyz1'] = (1,1,1)
        self._rowsPoint['xyz1'] = lambda c: (0,0,0)
        self._rowsCheck['xyz1'] = lambda c: (c[0] == c[1]) and (c[1] == c[2])
        self._rowsVect['xyz2'] = (-1,1,1)
        self._rowsPoint['xyz2'] = lambda c: (self._size-1,0,0)
        self._rowsCheck['xyz2'] = lambda c: (c[0] + c[1] == self._size-1) and (c[1] == c[2])
        self._rowsVect['xyz3'] = (1,-1,1)
        self._rowsPoint['xyz3'] = lambda c: (0,self._size-1,0)
        self._rowsCheck['xyz3'] = lambda c: (c[0] == c[2]) and (c[0] + c[1] == self._size-1)
        self._rowsVect['xyz4'] = (-1,-1,1)
        self._rowsPoint['xyz4'] = lambda c: (self._size-1,self._size-1,0)
        self._rowsCheck['xyz4'] = lambda c: (c[0] == c[1]) and (c[1] + c[2] == self._size-1)
        
    def __str__(self):
        return "3D grid instance with size " + str(self._size)
    
    def clear(self):
        """Clears the game grid"""
        for i in range(self._size):
            for j in range(self._size):
                for k in range(self._size):
                    self._table[i][j][k] = self._tokenFree
        self._winningCoordinates = [(-1,-1,-1) for k in range(self._size)]

    def is_free(self, c):
        """Checks if the given coordinates c = (x,y,z) point to a free space"""
        x,y,z = c
        return self._table[x][y][z] == self._tokenFree
    
    def set_grid_element(self, c, player):
        """Set the point at the given coordinates c = (x,y,z) with the player token"""
        x = max(0, min(self._size - 1, c[0]))
        y = max(0, min(self._size - 1, c[1]))
        z = max(0, min(self._size - 1, c[2]))
        if player == 0:
            if self._table[x][y][z] != self._tokenFree:
                self._gridFilling -= 1
            self._table[x][y][z] = self._tokenFree
        elif player == 1:
            if self._table[x][y][z] == self._tokenFree:
                self._gridFilling += 1
            self._table[x][y][z] = self._tokenPlayer1
        elif player == 2:
            if self._table[x][y][z] == self._tokenFree:
                self._gridFilling += 1
            self._table[x][y][z] = self._tokenPlayer2
    
    def check_row(self, point, vector):
        """Returns True and updates _winningCoordinates if the given row is a winning one, False if not
        The row is specified by starting point + directionnal vector"""
        x,y,z = point
        vx, vy, vz = vector
        t = self._table[x][y][z]
        for k in range(self._size):
            if self._table[x + k*vx][y + k*vy][z + k*vz] != t:
                break
        else:
            self._winningCoordinates = [(x + k*vx, y + k*vy, z + k*vz) for k in range(self._size)]
            return True
        return False


class Game:
    def __init__(self, player1, player2, gameSize = 3, is2D = False):
        self._gameSize = gameSize
        self._is2D = is2D
        if is2D:
            self._grid = Grid2D(gameSize)
        else:
            self._grid = Grid3D(gameSize)
        self._player1 = player1
        self._player2 = player2
        player1.game = self
        player2.game = self
        self._message = 'New game created'
        self._turn = 0
        
    def __str__(self):
        return "Game instance"
    
    def _get_gameSize(self):
        return self._gameSize
    gameSize = property(_get_gameSize)
    
    def _get_is2D(self):
        return self._is2D
    is2D = property(_get_is2D)
    
    def _get_grid(self):
        return self._grid
    grid = property(_get_grid)
    
    def _get_player1(self):
        return self._player1
    player1 = property(_get_player1)
    
    def _get_player2(self):
        return self._player2
    player2 = property(_get_player2)
    
    def _get_message(self):
        return self._message
    message = property(_get_message)
        
    def start(self, playerStartingFirst = 1):
        self._grid.clear()
        self._player1.clear_history()
        self._player2.clear_history()
        if playerStartingFirst == 1:
            self._message = 'Starting. It\'s player 1\'s (' + self._player1.name + ') turn.'
            self._turn = 1
        else:
            self._message = 'Starting. It\'s player 2\'s (' + self._player2.name + ') turn.'
            self._turn = 2
            
    def end(self):
        pass
    
    def play_coordinates(self, c, player):
        """The given player tries to play at coordinates c
        Exit codes:
            0: player is not player1 or player2
            1: space is not free
            2: not player's turn
            3: valid play, games continue
            4: valid play, victory
            5: valid play, draw (grid full with no victory)"""
        if player == self._player1 or player == self._player2:
            p = 1 if player == self._player1 else 2
            if (self._turn != 1 and player == self._player1) or (self._turn != 2 and player == self._player2):
                self._message = 'Not player ' + str(p) + '\'s turn'
                return 2
            if self._grid.is_free(c):
                self._grid.set_grid_element(c,p)
                self._message = 'Player ' + str(p) + ' (' + player.name + ') played in ' + str(c)
            else:
                self._message = 'Space ' + str(c) + 'is not free'
                return 1
        else:
            self._message = 'Invalid player.'
            return 0
        if self._grid.check_victory(c):
            self._message += ' Player ' + player.name + ' has won. Winning coordinates : ' + str(self._grid.winningCoordinates)
            return 4
        elif self._grid.is_full():
            self._message += ' Grid is full. Draw.'
            return 5
        else:
            if self._turn == 1:
                self._message += " It's player 2 (" + self._player2.name + ') turn now.'
                self._turn = 2
            else:
                self._message += " It's player 1 (" + self._player1.name + ') turn now.'
                self._turn = 1
            return 3
















