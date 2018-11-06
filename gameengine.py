#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
An implementation of a tic-tac-toe engine.
Manages classic 2D and 3D grids
Grids are n*n (or n*n*n) where n is an integer >= 1

Usage example:

p1 = Player("Alice")
p2 = Player("Bob")

g = Game(p1, p2, gameSize = 3, is2D = True)
g.start()

exit_code = p1.play((1,0,2))

print(g.message)

# do something depending on the exit code

"""


class Player:
    """Player
    
    Attributes:
        game (Game): the game in which the player is playing (read/write)
        name (str): player's name (read only)
        
    """

    def __init__(self, name):
        if type(name) != str:
            raise TypeError("Argument 'name': expected 'str', got " + str(type(name)))
        if len(name) > 30:
            raise ValueError("Name too long (maximum lentgh = 30)")
        self.__game = None
        self.__name = name

    def play(self, c):
        """Player tries to play at c = (x,y,z)
        Exit codes:
            0: player is not player 1 or player 2 of the game / player has no game
            1: space is not free
            2: not player's turn
            3: valid play, games continue
            4: valid play, victory
            5: valid play, draw (grid full with no victory)"""
        if self.__game is not None:
            if type(c) != tuple:
                raise TypeError("Argument 'c': expected 'tuple', got " + str(type(c)))
            if len(c) != 3 and self.__game.is2D == False:
                raise ValueError("Argument c should have 3 elements, but has " + str(len(c)))
            if len(c) != 2 and self.__game.is2D == True:
                raise ValueError("Argument c should have 2 elements, but has " + str(len(c)))
            return self.__game.play_coordinates(c, self)
        return 0

    def __str__(self):
        return self.__name

    def __get_game(self):
        return self.__game

    def __set_game(self, g):
        if not isinstance(g, Game):
            raise TypeError("Argument 'g' is not an instance of class 'Game'")
        self.__game = g

    game = property(__get_game, __set_game)

    def __get_name(self):
        return self.__name

    name = property(__get_name)


class Grid:
    """The game grid
    
    Attributes:
        size (int): number of cells in a row (read only)
        table (list): the actual grid (read only)
        winningCoordinates (list): the coordinates of each cell in the winning row. empty until victory (read only)
        
    Note:
        this class is just a base, its children Grid2D and Grid3D are actually useful
        
    """

    def __init__(self, size):
        if type(size) != int:
            raise TypeError("Argument 'size': expected 'int', got " + str(type(size)))
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
                if self._check_row(self._rowsPoint[code](playingPoint), self._rowsVect[code]):
                    return True
        return False

    def _check_row(self, point, vector):
        return False


class Grid2D(Grid):
    """The 2D game grid
    
    Attributes:
        size (int): number of cells in a row (read only)
        table (list): the actual grid (read only)
        winningCoordinates (list): the coordinates of each cell in the winning row. empty until victory (read only)
        
    Note:
        Inherit from Grid
        
    """

    def __init__(self, size):
        Grid.__init__(self, size)
        self._table = [[self._tokenFree for y in range(self._size)] for x in range(self._size)]
        self._winningCoordinates = [(-1, -1) for k in range(self._size)]
        self._gridCapacity = self._size ** 2
        self._rowsCodes = ['h', 'v', 'd1', 'd2']
        self._rowsVect['h'] = (1, 0)
        self._rowsPoint['h'] = lambda c: (0, c[1])
        self._rowsCheck['h'] = lambda c: True
        self._rowsVect['v'] = (0, 1)
        self._rowsPoint['v'] = lambda c: (c[0], 0)
        self._rowsCheck['v'] = lambda c: True
        self._rowsVect['d1'] = (1, 1)
        self._rowsPoint['d1'] = lambda c: (0, 0)
        self._rowsCheck['d1'] = lambda c: c[0] == c[1]
        self._rowsVect['d2'] = (1, -1)
        self._rowsPoint['d2'] = lambda c: (0, self._size - 1)
        self._rowsCheck['d2'] = lambda c: c[0] + c[1] == self._size - 1

    def __str__(self):
        return "2D grid instance with size " + str(self._size)

    def clear(self):
        """Clears the game grid"""
        for i in range(self._size):
            for j in range(self._size):
                self._table[i][j] = self._tokenFree
        self._winningCoordinates = [(-1, -1) for k in range(self._size)]

    def is_free(self, c):
        """Checks if the given coordinates c = (x,y) point to a free space"""
        if type(c) != tuple:
                raise TypeError("Argument 'c': expected 'tuple', got " + str(type(c)))
        if len(c) != 2:
            raise ValueError("Tuple c should have 2 elements, but has " + str(len(c)))
        x, y = c
        return self._table[x][y] == self._tokenFree

    def set_grid_element(self, c, player):
        """Set the point at the given coordinates c = (x,y) with the player token"""
        if type(c) != tuple:
                raise TypeError("Argument 'c': expected 'tuple', got " + str(type(c)))
        if len(c) != 2:
            raise ValueError("Tuple 'c' should have 2 elements, but has " + str(len(c)))
        if player not in (0, 1, 2):
            raise ValueError("Argument 'player' should be 0, 1 or 2")
        x, y = c
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

    def _check_row(self, point, vector):
        """Returns True and updates _winningCoordinates if the given row is a winning one, False if not
        The row is specified by starting point + directional vector"""
        x, y = point
        vx, vy = vector
        t = self._table[x][y]
        for k in range(self._size):
            if self._table[x + k * vx][y + k * vy] != t:
                break
        else:
            self._winningCoordinates = [(x + k * vx, y + k * vy) for k in range(self._size)]
            return True
        return False


class Grid3D(Grid):
    """The 3D game grid
    
    Attributes:
        size (int): number of cells in a row (read only)
        table (list): the actual grid (read only)
        winningCoordinates (list): the coordinates of each cell in the winning row. empty until victory (read only)

    Note:
        Inherit from Grid
        
    """

    def __init__(self, size):
        Grid.__init__(self, size)
        self._table = [[[self._tokenFree for z in range(self._size)] for y in range(self._size)] for x in
                       range(self._size)]
        self._winningCoordinates = [(-1, -1, -1) for k in range(self._size)]
        self._gridCapacity = self._size ** 3
        self._rowsCodes = ['x', 'y', 'z', 'xy1', 'xy2', 'xz1', 'xz2', 'yz1', 'yz2', 'xyz1', 'xyz2', 'xyz3', 'xyz4']
        self._rowsVect['x'] = (1, 0, 0)
        self._rowsPoint['x'] = lambda c: (0, c[1], c[2])
        self._rowsCheck['x'] = lambda c: True
        self._rowsVect['y'] = (0, 1, 0)
        self._rowsPoint['y'] = lambda c: (c[0], 0, c[2])
        self._rowsCheck['y'] = lambda c: True
        self._rowsVect['z'] = (0, 0, 1)
        self._rowsPoint['z'] = lambda c: (c[0], c[1], 0)
        self._rowsCheck['z'] = lambda c: True
        self._rowsVect['xy1'] = (1, 1, 0)
        self._rowsPoint['xy1'] = lambda c: (0, 0, c[2])
        self._rowsCheck['xy1'] = lambda c: c[0] == c[1]
        self._rowsVect['xy2'] = (1, -1, 0)
        self._rowsPoint['xy2'] = lambda c: (0, self._size - 1, c[2])
        self._rowsCheck['xy2'] = lambda c: c[0] + c[1] == self._size - 1
        self._rowsVect['xz1'] = (1, 0, 1)
        self._rowsPoint['xz1'] = lambda c: (0, c[1], 0)
        self._rowsCheck['xz1'] = lambda c: c[0] == c[2]
        self._rowsVect['xz2'] = (1, 0, -1)
        self._rowsPoint['xz2'] = lambda c: (0, c[1], self._size - 1)
        self._rowsCheck['xz2'] = lambda c: c[0] + c[2] == self._size - 1
        self._rowsVect['yz1'] = (0, 1, 1)
        self._rowsPoint['yz1'] = lambda c: (c[0], 0, 0)
        self._rowsCheck['yz1'] = lambda c: c[2] == c[1]
        self._rowsVect['yz2'] = (0, 1, -1)
        self._rowsPoint['yz2'] = lambda c: (c[0], 0, self._size - 1)
        self._rowsCheck['yz2'] = lambda c: c[2] + c[1] == self._size - 1
        self._rowsVect['xyz1'] = (1, 1, 1)
        self._rowsPoint['xyz1'] = lambda c: (0, 0, 0)
        self._rowsCheck['xyz1'] = lambda c: (c[0] == c[1]) and (c[1] == c[2])
        self._rowsVect['xyz2'] = (-1, 1, 1)
        self._rowsPoint['xyz2'] = lambda c: (self._size - 1, 0, 0)
        self._rowsCheck['xyz2'] = lambda c: (c[0] + c[1] == self._size - 1) and (c[1] == c[2])
        self._rowsVect['xyz3'] = (1, -1, 1)
        self._rowsPoint['xyz3'] = lambda c: (0, self._size - 1, 0)
        self._rowsCheck['xyz3'] = lambda c: (c[0] == c[2]) and (c[0] + c[1] == self._size - 1)
        self._rowsVect['xyz4'] = (-1, -1, 1)
        self._rowsPoint['xyz4'] = lambda c: (self._size - 1, self._size - 1, 0)
        self._rowsCheck['xyz4'] = lambda c: (c[0] == c[1]) and (c[1] + c[2] == self._size - 1)

    def __str__(self):
        return "3D grid instance with size " + str(self._size)

    def clear(self):
        """Clears the game grid"""
        for i in range(self._size):
            for j in range(self._size):
                for k in range(self._size):
                    self._table[i][j][k] = self._tokenFree
        self._winningCoordinates = [(-1, -1, -1) for k in range(self._size)]

    def is_free(self, c):
        """Checks if the given coordinates c = (x,y,z) point to a free space"""
        if type(c) != tuple:
                raise TypeError("Argument 'c': expected 'tuple', got " + str(type(c)))
        if len(c) != 3:
            raise ValueError("Tuple c should have 3 elements, but has " + str(len(c)))
        x, y, z = c
        return self._table[x][y][z] == self._tokenFree

    def set_grid_element(self, c, player):
        """Set the point at the given coordinates c = (x,y,z) with the player token"""
        if type(c) != tuple:
                raise TypeError("Argument 'c': expected 'tuple', got " + str(type(c)))
        if len(c) != 3:
            raise ValueError("Tuple 'c' should have 3 elements, but has " + str(len(c)))
        if player not in (0, 1, 2):
            raise ValueError("Argument 'player' should be 0, 1 or 2")
        x, y, z = c
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

    def _check_row(self, point, vector):
        """Returns True and updates _winningCoordinates if the given row is a winning one, False if not
        The row is specified by starting point + directionnal vector"""
        x, y, z = point
        vx, vy, vz = vector
        t = self._table[x][y][z]
        for k in range(self._size):
            if self._table[x + k * vx][y + k * vy][z + k * vz] != t:
                break
        else:
            self._winningCoordinates = [(x + k * vx, y + k * vy, z + k * vz) for k in range(self._size)]
            return True
        return False


class Game:
    """The tic-tac-toe game
    
    Attributes:
        gameSize (int): number of cells in a row (read only)
        is2D (bool): true -> 2D game, false -> 3D game (read only)
        grid (Grid): the Grid instance of the game (read only)
        player1 (Player): the first player of the game (read only)
        player2 (Player): the second player of the game (read only)
        message (str): a string indicating the current game status
        
    Note:
        The two players should be different instances of Player
        
    """

    def __init__(self, player1, player2, gameSize=3, is2D=False):
        if not (isinstance(player1, Player) and isinstance(player2, Player)):
            raise TypeError("Arguments players are not instances of class 'Player'")
        if player1 == player2:
            raise ValueError("Player1 and 2 should not be the same")
        if type(gameSize) != int:
            raise TypeError("Argument 'gameSize': expected 'int', got " + str(type(gameSize)))
        if not (1 <= gameSize <= 9):
            raise ValueError("Argument 'gameSize' out of bounds, wanted [1,9], got " + str(gameSize))
        if type(is2D) != bool:
            raise TypeError("Argument 'is2D': expected 'bool', got " + str(type(is2D)))
        self.__gameSize = gameSize
        self.__is2D = is2D
        if is2D:
            self.__grid = Grid2D(gameSize)
        else:
            self.__grid = Grid3D(gameSize)
        self.__player1 = player1
        self.__player2 = player2
        player1.game = self
        player2.game = self
        self.__message = 'New game created'
        self.__turn = 0

    def start(self, playerPlayingFirst=1):
        """Initializes the game. This method must be called before playing.
        
        Arg: 
            playerPlayingFirst (int): 1 -> player1 starts, 2 -> player2 starts
        
        """
        if not playerPlayingFirst in (1, 2):
            raise ValueError("Argument 'playerPlayingFirst' should be 1 or 2, got " + str(playerPlayingFirst))
        self.__grid.clear()
        if playerPlayingFirst == 1:
            self.__message = 'Starting. It\'s player 1\'s (' + self.__player1.name + ') turn.'
            self.__turn = 1
        else:
            self.__message = 'Starting. It\'s player 2\'s (' + self.__player2.name + ') turn.'
            self.__turn = 2

    def play_coordinates(self, c, player):
        """The given player tries to play at coordinates c
        Exit codes:
            0: player is not player1 or player2
            1: space is not free
            2: not player's turn
            3: valid play, games continue
            4: valid play, victory
            5: valid play, draw (grid full with no victory)"""
        if not isinstance(player, Player):
            raise TypeError("Argument 'player' should be an instance of class 'Player', got " + str(type(player)))
        if player == self.__player1 or player == self.__player2:
            p = 1 if player == self.__player1 else 2
            if (self.__turn != 1 and player == self.__player1) or (self.__turn != 2 and player == self.__player2):
                self.__message = 'Not player ' + str(p) + '\'s turn'
                return 2
            if self.__grid.is_free(c):
                self.__grid.set_grid_element(c, p)
                self.__message = 'Player ' + str(p) + ' (' + player.name + ') played in ' + str(c)
            else:
                self.__message = 'Space ' + str(c) + ' is not free'
                return 1
        else:
            self.__message = 'Invalid player.'
            return 0
        if self.__grid.check_victory(c):
            self.__message += ' Player ' + player.name + ' has won. Winning coordinates : ' + str(
                self.__grid.winningCoordinates)
            return 4
        elif self.__grid.is_full():
            self.__message += ' Grid is full. Draw.'
            return 5
        else:
            if self.__turn == 1:
                self.__message += " It's player 2 (" + self.__player2.name + ') turn now.'
                self.__turn = 2
            else:
                self.__message += " It's player 1 (" + self.__player1.name + ') turn now.'
                self.__turn = 1
            return 3

    def __get_gameSize(self):
        return self.__gameSize

    gameSize = property(__get_gameSize)

    def __get_is2D(self):
        return self.__is2D

    is2D = property(__get_is2D)

    def __get_grid(self):
        return self.__grid

    grid = property(__get_grid)

    def __get_player1(self):
        return self.__player1

    player1 = property(__get_player1)

    def __get_player2(self):
        return self.__player2

    player2 = property(__get_player2)

    def __get_message(self):
        return self.__message

    message = property(__get_message)
