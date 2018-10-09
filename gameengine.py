#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 10:09:31 2018

@author: armand
"""

class Player:
    
    def __init__(self, name):
        self.game = None
        self.name = name
    
    def play(self, c):
        """Player tries to play at c = (x,y,z)"""
        if self.game:
            self.game.play_coordinates(c, self)

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
        self.size = size
        self.tokenFree = 0
        self.tokenPlayer1 = 1
        self.tokenPlayer2 = 2
        

class Grid2D(Grid):
    def __init__(self, size):
        Grid.__init__(self, size)
        self.table = [[self.tokenFree for y in range(self.size)] for x in range(self.size)]
        self.winningCoordinates = [(-1,-1) for k in range(self.size)]
        
    def clear(self):
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
        vx, vy = vector
        t = self.table[x][y]
        for k in range(self.size):
            v = v and (self.table[x][y] == t)
            x += vx
            y += vy
        return v
    
    def check_victory(self, playingPoint):
        """Checks if the given points is in a victorious row
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
            if self.check_row((0,self.size-1), (1,-1)):
                self.winningCoordinates = [(k, self.size - k - 1) for k in range(self.size)]
                return True
        return False

        
class Grid3D(Grid):
    def __init__(self, size):
        Grid.__init__(self, size)
        self.table = [[[self.tokenFree for z in range(self.size)] for y in range(self.size)] for x in range(self.size)]
        self.winningCoordinates = [(-1,-1,-1) for k in range(self.size)]
        
    def clear(self):
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
        vx, vy, vz = vector
        t = self.table[x][y][z]
        for k in range(self.size):
            v = v and (self.table[x][y][z] == t)
            x += vx
            y += vy
            z += vz
        return v
    
    def check_victory(self, playingPoint):
        """Checks if the given points is in a victorious row
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
            if self.check_row((0,self.size - 1,z), (1,-1,0)):
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
            if self.check_row((0,y,self.size - 1), (1,0,-1)):
                self.winningCoordinates = [(k, y, self.size - k - 1) for k in range(self.size)]
                return True
        if y == z:
            if self.check_row((x,0,0), (0,1,1)):
                self.winningCoordinates = [(x,k,k) for k in range(self.size)]
                return True
        if y + z == self.size - 1:
            if self.check_row((x,0,self.size - 1), (0,1,-1)):
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
        self.player1 = player1
        self.player2 = player2
        self.player1History = []
        self.player2History = []
        player1.game = self
        player2.game = self
        self.message = 'New game created'
        self.turn = 0
        
    def start(self, playerStartingFirst = 1):
        self.grid.clear()
        self.player1History = []
        self.player2History = []
        if playerStartingFirst == 1:
            self.message = 'Starting. It\'s player ' + self.player1.name + '\'s turn.'
            self.turn = 1
        else:
            self.message = 'Starting. It\'s player ' + self.player2.name + '\'s turn.'
            self.turn = 2
            
    def end(self):
        pass
    
    def play_coordinates(self, c, player):
        success = False
        if player == self.player1 and self.turn == 1:
            if self.is2D:
                x,y = c
                if self.grid.is_free(x,y):
                    self.grid.table[x][y] = self.grid.tokenPlayer1
                    self.player1History.append(c)
                    self.message = 'Player ' + self.player1.name + ' played in ' + str(c) + '.'
                    success = True
                else:
                    self.message = 'The given coordinates do not point to a free space in the grid.'
            else:
                x,y,z = c
                if self.grid.is_free(x,y,z):
                    self.grid.table[x][y][z] = self.grid.tokenPlayer1
                    self.player1History.append(c)
                    self.message = 'Player ' + self.player1.name + ' played in ' + str(c) + '.'
                    success = True
                else:
                    self.message = 'The given coordinates do not point to a free space in the grid.'
        elif player == self.player2 and self.turn == 2:
            if self.is2D:
                x,y = c
                if self.grid.is_free(x,y):
                    self.grid.table[x][y] = self.grid.tokenPlayer2
                    self.player2History.append(c)
                    self.message = 'Player ' + self.player2.name + ' played in ' + str(c) + '.'
                    success = True
                else:
                    self.message = 'The given coordinates do not point to a free space in the grid.'
            else:
                x,y,z = c
                if self.grid.is_free(x,y,z):
                    self.grid.table[x][y][z] = self.grid.tokenPlayer2
                    self.player2History.append(c)
                    self.message = 'Player ' + self.player2.name + ' played in ' + str(c) + '.'
                    success = True
                else:
                    self.message = 'The given coordinates do not point to a free space in the grid.'
        else:
            self.message = 'Invalid player.'
        if success:
            if self.grid.check_victory(c):
                self.message += ' Player ' + player.name + ' has won. Winning coordinates : ' + str(self.grid.winningCoordinates)
                self.end(self)
            else:
                if self.turn == 1:
                    self.message += " It's player " + self.player2.name + "'s turn now."
                    self.turn = 2
                else:
                    self.message += " It's player " + self.player1.name + "'s turn now."
                    self.turn = 1
            return True
        else:
            return False


p1 = Player('Alice')
p2 = Player('Bob')
g = Game(p1, p2, 3, True)























