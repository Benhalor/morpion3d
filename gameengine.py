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
        Exit code:
            -1: invalid play
            0: valid play
            1: victory
            9: error"""
        if self.game:
            code = self._game.play_coordinates(c, self)
            if code in (1,2):
                return -1
            elif code == 3:
                return 0
            elif code == 4:
                return 1
        return 9
            

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
        self._winningCoordinates = []
        
    def _get_size(self):
        return self._size
    size = property(_get_size)
    
    def _get_table(self):
        return self._table
    table = property(_get_table)
    
    def _get_winningCoordinates(self):
        return self._winningCoordinates
    winningCoordinates = property(_get_winningCoordinates)
    

class Grid2D(Grid):
    def __init__(self, size):
        Grid.__init__(self, size)
        self._table = [[self._tokenFree for y in range(self._size)] for x in range(self._size)]
        self._winningCoordinates = [(-1,-1) for k in range(self._size)]
        
    def clear(self):
        """Clears the game grid"""
        for i in range(self._size):
            for j in range(self._size):
                self._table[i][j] = self._tokenFree
        self._winningCoordinates = [(-1,-1) for k in range(self._size)]
    
    def is_free(self, x, y):
        """Checks if the given coordinates point to a free space"""
        return self._table[x][y] == self._tokenFree
    
    def set_grid_element(self, x, y, player):
        """Set the point at the given coordinates with the player token"""
        x = max(0, min(self._size - 1, x))
        y = max(0, min(self._size - 1, y))
        if player == 0:
            self._table[x][y] = self._tokenFree
        elif player == 1:
            self._table[x][y] = self._tokenPlayer1
        elif player == 2:
            self._table[x][y] = self._tokenPlayer2

    
    def check_row(self, point, vector):
        """Returns True if the given row is a winning one, False if not
        The row is specified by starting point + directionnal vector"""
        v = True
        x,y = point
        vx, vy = vector
        t = self._table[x][y]
        for k in range(self._size):
            v = v and (self._table[x][y] == t)
            x += vx
            y += vy
        return v
    
    def check_victory(self, playingPoint):
        """Checks if the given points is in a victorious row
        Updates self._winningCoordinates if True"""
        x,y = playingPoint
        if self.check_row((0,y), (1,0)):
            self._winningCoordinates = [(k,y) for k in range(self._size)]
            return True
        if self.check_row((x,0), (0,1)):
            self._winningCoordinates = [(x,k) for k in range(self._size)]
            return True
        if x == y:
            if self.check_row((0,0), (1,1)):
                self._winningCoordinates = [(k,k) for k in range(self._size)]
                return True
        if x + y == self._size - 1:
            if self.check_row((0,self._size-1), (1,-1)):
                self._winningCoordinates = [(k, self._size - k - 1) for k in range(self._size)]
                return True
        return False

        
class Grid3D(Grid):
    def __init__(self, size):
        Grid.__init__(self, size)
        self.table = [[[self.tokenFree for z in range(self._size)] for y in range(self._size)] for x in range(self._size)]
        self._winningCoordinates = [(-1,-1,-1) for k in range(self._size)]
        
    def clear(self):
        """Clears the game grid"""
        for i in range(self._size):
            for j in range(self._size):
                for k in range(self._size):
                    self._table[i][j][k] = self._tokenFree
        self._winningCoordinates = [(-1,-1,-1) for k in range(self._size)]

    def is_free(self, x, y, z):
        """Checks if the given coordinates point to a free space"""
        return self._table[x][y][z] == self._tokenFree
    
    def set_grid_element(self, x, y, z, player):
        """Set the point at the given coordinates with the player token"""
        x = max(0, min(self._size - 1, x))
        y = max(0, min(self._size - 1, y))
        z = max(0, min(self._size - 1, z))
        if player == 0:
            self._table[x][y][z] = self._tokenFree
        elif player == 1:
            self._table[x][y][z] = self._tokenPlayer1
        elif player == 2:
            self._table[x][y][z] = self._tokenPlayer2
    
    def check_row(self, point, vector):
        """Returns True if the given row is a winning one, False if not
        The row is specified by starting point + directionnal vector"""
        v = True
        x,y,z = point
        vx, vy, vz = vector
        t = self._table[x][y][z]
        for k in range(self._size):
            v = v and (self._table[x][y][z] == t)
            x += vx
            y += vy
            z += vz
        return v
    
    def check_victory(self, playingPoint):
        """Checks if the given points is in a victorious row
        Updates self._winningCoordinates if True"""
        x,y,z = playingPoint
        if self.check_row((0,y,z), (1,0,0)):
            self._winningCoordinates = [(k,y,z) for k in range(self._size)]
            return True
        if self.check_row((x,0,z), (0,1,0)):
            self._winningCoordinates = [(x,k,z) for k in range(self._size)]
            return True
        if self.check_row((x,y,0), (0,0,1)):
            self._winningCoordinates = [(x,y,k) for k in range(self._size)]
            return True
        if x == y:
            if self.check_row((0,0,z), (1,1,0)):
                self._winningCoordinates = [(k,k,z) for k in range(self._size)]
                return True
            if y == z:
                if self.check_row((0,0,0), (1,1,1)):
                    self._winningCoordinates = [(k,k,k) for k in range(self._size)]
                    return True
            if y + z == self._size - 1:
                if self.check_row((0,0,self._size-1), (1,1,-1)):
                    self._winningCoordinates = [(k,k,self._size - k - 1) for k in range(self._size)]
                    return True
        if x + y == self._size - 1:
            if self.check_row((0,self._size - 1,z), (1,-1,0)):
                self._winningCoordinates = [(k, self._size - k - 1, z) for k in range(self._size)]
                return True
            if x == z:
                if self.check_row((0,self._size - 1,0), (1,-1,1)):
                    self._winningCoordinates = [(k,self._size - k - 1,k) for k in range(self._size)]
                    return True
            if y == z:
                if self.check_row((self._size - 1,0,0), (-1,1,1)):
                    self._winningCoordinates = [(self._size - k - 1,k,k) for k in range(self._size)]
                    return True
        if x == z:
            if self.check_row((0,y,0), (1,0,1)):
                self._winningCoordinates = [(k,y,k) for k in range(self._size)]
                return True
        if x + z == self._size - 1:
            if self.check_row((0,y,self._size - 1), (1,0,-1)):
                self._winningCoordinates = [(k, y, self._size - k - 1) for k in range(self._size)]
                return True
        if y == z:
            if self.check_row((x,0,0), (0,1,1)):
                self._winningCoordinates = [(x,k,k) for k in range(self._size)]
                return True
        if y + z == self._size - 1:
            if self.check_row((x,0,self._size - 1), (0,1,-1)):
                self._winningCoordinates = [(x,k, self._size - k - 1) for k in range(self._size)]
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
    
    def _get_gameSize(self):
        return self._gameSize
    gameSize = property(_get_gameSize)
    
    def _get_is2D(self):
        return self._is2D
    is2D = property(_get_is2D)
    
    def _get_grid(self):
        return self._grid
    gird = property(_get_grid)
    
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
            self.turn = 1
        else:
            self.message = 'Starting. It\'s player 2\'s (' + self._player2.name + ') turn.'
            self.turn = 2
            
    def end(self):
        pass
    
    def play_coordinates(self, c, player):
        """The given player tries to play at coordinates c
        Exit codes:
            0: player is not player1 or player2
            1: space is not free
            2: not player's turn
            3: valid play, games continue
            4: valid play, victory"""
        if player == self._player1 or player == self._player2:
            p = 1 if player == self._player1 else 2
            if (self._turn != 1 and player == self._player1) or (self._turn != 2 and player == self._player2):
                self._message = 'Not player ' + str(p) + '\'s turn'
                return 2
            if self._is2D:
                x,y = c
                if self._grid.is_free(x,y):
                    self._grid.set_grid_element(x,y,p)
                    self._message = 'Player ' + str(p) + ' (' + player.name + ') played in ' + str(c)
                else:
                    self._message = 'Space ' + str(c) + 'is not free'
                    return 1
            else:
                x,y,z = c
                if self._grid.is_free(x,y,z):
                    self._grid.set_grid_element(x,y,z,p)
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
        else:
            if self._turn == 1:
                self._message += " It's player 2 (" + self._player2.name + ') turn now.'
                self.turn = 2
            else:
                self._message += " It's player 1 (" + self._player1.name + ') turn now.'
                self.turn = 1
            return 3

























