import guiMainWindow
import gameengine
import traceback
from morpionExceptions import ServerError, GuiNotAliveError


class GameSession:
    def __init__(self, playerClient, playerName):
        self._myClient = playerClient  # client should be already connected
        self._playerName = playerName
        self._dimension = self._myClient.dimension
        self._matrixSize = self._myClient.matrixSize

        # Game engine
        self._me = gameengine.Player(self._playerName)
        self._opponent = gameengine.Player('Opponent')
        self._game = gameengine.Game(self._me, self._opponent, self._matrixSize, is2D=(self._dimension == 2))

        # GUI
        self._gui = guiMainWindow.MainWindow(self._dimension, self._matrixSize)
        self._gui.start()
        self._myClient.gui = self._gui

    def start_playing(self):
        """0: player is not player1 or player2
        1: space is not free
        2: not player's turn
        3: valid play, games continue
        4: valid play, victory
        5: valid play, draw (grid full with no victory)
        6: defeat
        7: other disconnected
        8: server disconnected
        9: stop"""

        # determine who is the first player

        state = 0
        playedCell = ""

        try:
            first = self._myClient.wait_first_cell(self._gui)
            if first:
                self._game.start(1)
            else:
                self._game.start(0)
            print("First " + str(first))
        except Exception as e:
            state = 9
            traceback.print_exc()



        while state < 4 and self._gui.is_alive():

            # Opponent play
            if self._gui.is_alive() and not first:
                try:
                    try:
                        playedCell = self._myClient.wait_the_other_to_play(self._gui)
                        opponent_state = self._opponent.play(playedCell)
                        print("Game session opponent state: " + str(opponent_state))
                        if opponent_state == 4:  # Opponent wins : it means that you lose
                            state = 6
                        elif opponent_state == 5:  # Opponent do draw
                            state = 5
                        self._gui.set_message(self._game.message)
                        matrix = self._game.grid.table
                        self._gui.send_state_matrix(matrix)
                    except GuiNotAliveError:
                        state = 9
                except ServerError:
                    state = 7
            else:
                first = False

            # Me play
            if state < 4:
                state = -1
            while state <= 2 and self._gui.is_alive():
                playedCell = self._gui.get_played_cell()
                if playedCell is not None and -1 not in playedCell:  # None if the windows is closed by user
                    state = self._me.play(playedCell)  # return -1 for invalid, 0 for valid, 1 for defeat, 2 for victory
                    self._gui.set_message(self._game.message)

            if self._gui.is_alive() and state <= 5:
                output = self._myClient.play(playedCell)
                if not output:  # Happens if server is disconnected
                    state = 7

                # Update GUI
                matrix = self._game.grid.table
                self._gui.send_state_matrix(matrix)

            print(state)

        return int(state)

    def _get_gui(self):
        return self._gui

    gui = property(_get_gui)

