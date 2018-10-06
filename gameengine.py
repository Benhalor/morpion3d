#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 10:09:31 2018

@author: armand
"""

class Player:
    
    def __init__(self, game, name):
        self.game = game
    
    def play(self, x, y, z):
        """Player tries to play at (x,y,z)"""
        pass

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
    def __init__(self, size, is2D):
        self.size = size
        self.tokenFree = 0
        self.tokenPlayer1 = 1
        self.tokenPlayer2 = 2
        

class Grid2D(Grid):
    def __init__(self, size):
        Grid.__init__(self, size)
        self.table = [[self.tokenFree for y in range(self.size)] for x in range(self.size)]
        self.winningCoordinates = [(-1,-1) for k in range(self.size)]
        
    def clear_grid(self):
        """Clears the game grid"""
        for i in range(self.size):
            for j in range(self.size):
                self.table[i][j] = self.tokenFree
        self.winningCoordinates = [(-1,-1) for k in range(self.size)]
    
    def is_free(self, x, y):
        """Checks if the given coordinates point to a free space"""
        return self.table[x][y] == self.tokenFree
    
    def check_row(self, point, vector):
        """Returns True if the given row is a winning one, False if not
        The row is specified by starting point + directionnal vector"""
        v = True
        x,y = point
        vx, vy = v
        t = self.table[x][y]
        for k in range(self.size):
            v = v and (self.table[x][y] == t)
            x += vx
            y += vy
        return v
    
    def check_victory(self, playingPoint, playingPlayer):
        """Checks if the given play will result in a victory
        Updates self.winningCoordinates if True"""
        x,y = playingPoint
        if self.check_row((0,y), (1,0)):
            self.winningCoordinates = [(k,y) for k in range(self.size)]
            return True
        if self.check_row((x,0), (0,1)):
            self.winningCoordinates = [(x,k) for k in range(self.size)]
            return True
        if x == y:
            if self.check_row((0,0), (1,1)):
                self.winningCoordinates = [(k,k) for k in range(self.size)]
                return True
        if x + y == self.size - 1:
            if self.check_row((0,self.size), (1,-1)):
                self.winningCoordinates = [(k, self.size - k - 1) for k in range(self.size)]
                return True
        return False

        
class Grid3D(Grid):
    def __init__(self, size):
        Grid.__init__(self, size)
        self.table = [[[self.tokenFree for z in range(self.size)] for y in range(self.size)] for x in range(self.size)]
        self.winningCoordinates = [(-1,-1,-1) for k in range(self.size)]
        
    def clear_grid(self):
        """Clears the game grid"""
        for i in range(self.size):
            for j in range(self.size):
                for k in range(self.size):
                    self.table[i][j][k] = self.tokenFree
        self.winningCoordinates = [(-1,-1,-1) for k in range(self.size)]

    def is_free(self, x, y, z):
        """Checks if the given coordinates point to a free space"""
        return self.table[x][y][z] == self.tokenFree
    
    def check_row(self, point, vector):
        """Returns True if the given row is a winning one, False if not
        The row is specified by starting point + directionnal vector"""
        v = True
        x,y,z = point
        vx, vy, vz = v
        t = self.table[x][y][z]
        for k in range(self.size):
            v = v and (self.table[x][y][z] == t)
            x += vx
            y += vy
            z += vz
        return v
    
    def check_victory(self, playingPoint, playingPlayer):
        """Checks if the given play will result in a victory
        Updates self.winningCoordinates if True"""
        x,y,z = playingPoint
        if self.check_row((0,y,z), (1,0,0)):
            self.winningCoordinates = [(k,y,z) for k in range(self.size)]
            return True
        if self.check_row((x,0,z), (0,1,0)):
            self.winningCoordinates = [(x,k,z) for k in range(self.size)]
            return True
        if self.check_row((x,y,0), (0,0,1)):
            self.winningCoordinates = [(x,y,k) for k in range(self.size)]
            return True
        if x == y:
            if self.check_row((0,0,z), (1,1,0)):
                self.winningCoordinates = [(k,k,z) for k in range(self.size)]
                return True
            if y == z:
                if self.check_row((0,0,0), (1,1,1)):
                    self.winningCoordinates = [(k,k,k) for k in range(self.size)]
                    return True
            if y + z == self.size - 1:
                if self.check_row((0,0,self.size-1), (1,1,-1)):
                    self.winningCoordinates = [(k,k,self.size - k - 1) for k in range(self.size)]
                    return True
        if x + y == self.size - 1:
            if self.check_row((0,self.size,z), (1,-1,0)):
                self.winningCoordinates = [(k, self.size - k - 1, z) for k in range(self.size)]
                return True
            if x == z:
                if self.check_row((0,self.size - 1,0), (1,-1,1)):
                    self.winningCoordinates = [(k,self.size - k - 1,k) for k in range(self.size)]
                    return True
            if y == z:
                if self.check_row((self.size - 1,0,0), (-1,1,1)):
                    self.winningCoordinates = [(self.size - k - 1,k,k) for k in range(self.size)]
                    return True
        if x == z:
            if self.check_row((0,y,0), (1,0,1)):
                self.winningCoordinates = [(k,y,k) for k in range(self.size)]
                return True
        if x + z == self.size - 1:
            if self.check_row((0,y,self.size), (1,0,-1)):
                self.winningCoordinates = [(k, y, self.size - k - 1) for k in range(self.size)]
                return True
        if y == z:
            if self.check_row((x,0,0), (0,1,1)):
                self.winningCoordinates = [(x,k,k) for k in range(self.size)]
                return True
        if y + z == self.size - 1:
            if self.check_row((x,0,self.size), (0,1,-1)):
                self.winningCoordinates = [(x,k, self.size - k - 1) for k in range(self.size)]
                return True
        return False

class Game:
    def __init__(self, player1, player2, gameSize = 3, is2D = False):
        self.gameSize = gameSize
        self.is2D = is2D
        if is2D:
            self.grid = Grid2D(gameSize)
        else:
            self.grid = Grid3D(gameSize)
        
      


























