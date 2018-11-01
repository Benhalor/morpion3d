import guiMainWindow
import gameengine
from morpionExceptions import ServerError, GuiNotAliveError


class GameSession:
    """GameSession
    One gamesession for each game.

    Method:
        start_playing (GameSession): start a game and returns an exit code depending on the state of the game at the end

    Usage example:

    session = gamesession.GameSession(playerClient, name)
    exit_code = session.start_playing()
    """
    def __init__(self, playerClient, playerName):
        self.__myClient = playerClient  # client should be already connected
        self.__playerName = playerName
        self.__matrixSize = self.__myClient.matrixSize

        # Game engine
        self.__me = gameengine.Player(self.__playerName)
        self.__opponent = gameengine.Player('Opponent')
        self.__game = gameengine.Game(self.__me, self.__opponent, self.__matrixSize)

        # GUI
        self.__gui = guiMainWindow.MainWindow(self.__matrixSize)
        self.__gui.start()
        self.__myClient.gui = self.__gui

    def start_playing(self):
        """State Table
        0: player is not player1 or player2
        1: space is not free
        2: not player's turn
        3: valid play, games continue
        4: valid play, victory
        5: valid play, draw (grid full with no victory)
        6: defeat
        7: other disconnected
        8: server disconnected
        9: windows closed"""

        state = 0
        playedCell = ""

        # Start
        try:
            # Wait for starting message from server. First = True -> you are the first player
            first = self.__myClient.wait_for_start(self.__gui)
            if first:
                self.__game.start(1)
            else:
                self.__game.start(2)
            print("First " + str(first))
        except Exception as e:
            state = 7

        # Playing loop until game is finished (state >=4)
        while state < 4 and self.__gui.is_alive():

            # Opponent play
            if self.__gui.is_alive() and not first:
                try:
                    try:
                        # Wait the other to play and get the cell played by other player
                        playedCell = self.__myClient.wait_the_other_to_play(self.__gui)

                        # Send this cell in the game engine
                        opponent_state = self.__opponent.play(playedCell)
                        print("Game session opponent state: " + str(opponent_state))
                        if opponent_state == 4:  # Opponent wins : it means that you lose
                            state = 6
                        elif opponent_state == 5:  # Opponent do draw
                            state = 5

                        # Update gui message and grid
                        self.__gui.textMessage = self.__game.message
                        matrix = self.__game.grid.table
                        self.__gui.highlight_played_cell(tuple(playedCell))
                        self.__gui.send_state_matrix(matrix)
                    except GuiNotAliveError:
                        state = 9
                except ServerError:
                    state = 8
            else:
                first = False

            # Me play only if the game is not finished (state <4) and do while loop until valid play
            if state < 4:
                state = -1
            while state <= 2 and self.__gui.is_alive():
                playedCell = self.__gui.get_played_cell()
                # None if the windows is closed by user, -1 if player click outside the grid
                if playedCell is not None and -1 not in playedCell:
                    state = self.__me.play(playedCell)
                    self.__gui.textMessage = self.__game.message
                if playedCell is None:
                    state = 9

            if self.__gui.is_alive() and state <= 5:
                output = self.__myClient.play(playedCell)
                if not output:  # Happens if server is disconnected
                    state = 7

                # Update GUI
                matrix = self.__game.grid.table
                self.__gui.highlight_played_cell(tuple(playedCell))
                self.__gui.send_state_matrix(matrix)

        if not self.__gui.isAlive():
            state = 9

        # In case of win or defeat
        if state == 4 or state == 6:
            print("Game session highlight")
            for coordinate in self.__game.grid.winningCoordinates:
                self.__gui.highlight_winning_cell(coordinate)
        return int(state)

    def __get_gui(self):
        return self.__gui

    gui = property(__get_gui)
