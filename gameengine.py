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
        self.is2D = is2D
        self.token = {"free":0, "player1":1, "player2":2}
        if self.is2D:
            self.table = [[self.token['free'] for y in range(self.size)] for x in range(self.size)]
        else:
            self.table = [[[self.token['free'] for z in range(self.size)] for y in range(self.size)] for x in range(self.size)]
        
    def clear_grid(self):
        """Clears the game grid"""
        for i in range(self.size):
            for j in range(self.size):
                if self.is2D:
                    self.table[i][j] = self.token['free']
                else:
                    for k in range(self.size):
                        self.table[i][j][k] = self.token['free']
    
    def is_free(self, coordinates):
        """Checks if the given coordinates point to a free space"""
        if self.is2D:
            x,y = coordinates
            return self.table[x][y] == self.token['free']
                
        else:
            x,y,z = coordinates
            return self.table[x][y][z] == self.token['free']
    
    def check_victory(self, coordinates, playerPlaying):
        """Checks victory status and returns the winning coordinates in a list
        coordinates : tuple of the tested coordinates, eg: (1,2) or (1,2,2)
        playerPlaying : string can be 'player1' or 'player2'"""
        if self.is2D:
            x,y = coordinates
            
            #horizontally
            L = []
            v = True
            for k in range(self.size):
                v = v and (self.table[k][y] == self.token[playerPlaying])
                L.append((k,y))
            if v:
                return True, L
            
            #vertically
            L = []
            v = True
            for k in range(self.size):
                v = v and (self.table[x][k] == self.token[playerPlaying])
                L.append((x,k))
            if v:
                return True, L
            
            #first diagonal
            if x == y:
                L = []
                v = True
                for k in range(self.size):
                    v = v and (self.table[k][k] == self.token[playerPlaying])
                if v:
                    return True, L
            
            #second diagonal
            if x + y == self.size - 1:
                L = []
                v = True
                for k in range(self.size):
                    v = v and (self.table[k][self.size - k] == self.token[playerPlaying])
                if v:
                    return True, L
                
        else:
            x,y,z = coordinates
            
            #along x
            L = []
            v = True
            for k in range(self.size):
                v = v and (self.table[k][y][z] == self.token[playerPlaying])
                L.append((k,y))
            if v:
                return True, L
            
            #along y
            L = []
            v = True
            for k in range(self.size):
                v = v and (self.table[x][k][z] == self.token[playerPlaying])
                L.append((x,k))
            if v:
                return True, L
            
            #along z
            L = []
            v = True
            for k in range(self.size):
                v = v and (self.table[x][y][k] == self.token[playerPlaying])
                L.append((x,k))
            if v:
                return True, L
            
            #fais mon idée géniale
            #point de départ + vecteur de déplacement
            #c'est mieux que 35 conditions
    

class Game:
    def __init__(self, player1, player2, gameSize = 3, is2D = False):
        self.gameSize = gameSize
        self.is2D = is2D
        self.grid = Grid(gameSize, is2D)
        
      
        
        
        
        
        
    def check_new_status(self, newCoordinates, playerPlayingName):
        """Checks the game status with the new coordinates, assuming the current grid is valid"""
        if self.is2D:
            x,y = newCoordinates
            if self.grid[x][y] != self.token['free']:
                return self.status['invalid']
        else:
            pass

























