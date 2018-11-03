import gameengine
from morpionExceptions import *


class GameSession:
    """GameSession
    One gamesession for each game.

    """
    def __init__(self, data):
        self.__data = data
        self.__stopBool = False
        self.__state = -1

        # Game engine
        self.__me = gameengine.Player('local player')
        self.__opponent = gameengine.Player('opponent')
        self.__game = gameengine.Game(self.__me, self.__opponent, self.__data.gameSize)
        self.__game.start(self.__data.starting)
        

    def play_a_turn(self, playerNumber, playingCell):
        """State Table
        0: player is not player1 or player2
        1: space is not free
        2: not player's turn
        3: valid play, games continue
        4: valid play, victory
        5: valid play, draw (grid full with no victory)
        """
        
        player = self.__me if playerNumber == 1 else self.__opponent
        
        self.__state = player.play(playingCell)
        
        if self.__state in (0, 2):
            raise GameError()
        
        if self.__state in (3, 4, 5):
            self.__data.window.highlight_played_cell(playingCell)
            self.__data.window.send_grid(self.__game.grid.table)
        
        if self.__state == 4:
            for cell in self.__game.grid.winningCoordinates:
                self.__data.window.highlight_winning_cell(cell)
        
        
    
    def __get_state(self):
        return self.__state
    state = property(__get_state)
