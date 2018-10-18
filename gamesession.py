import guiMainWindow
import gameengine

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

    def start_playing(self):
        """0: player is not player1 or player2
        1: space is not free
        2: not player's turn
        3: valid play, games continue
        4: valid play, victory
        5: valid play, draw (grid full with no victory)
        6: defeat
        7: other disconnected
        8: server disconnected"""

        # determine who is the first player
        played_cell = self._myClient.wait_the_other_to_play(self._gui)
        if -1 in played_cell:
            self._game.start(1)
        else:
            self._game.start(0)

        state = 0
        while state < 4 and self._gui.is_alive():

            # Opponent play
            if "OTHER_DISCONNECTED" in played_cell:
                state = 6
            else:
                if self._gui.is_alive() and -1 not in played_cell:  # -1 if nothing to update (normally happens only if you at the first cell)
                    opponent_state = self._opponent.play(played_cell)
                    print("Game session opponent state: "+str(opponent_state))
                    if opponent_state == 4:  # Opponent wins : it means that you lose
                        state = 6
                    elif opponent_state == 5: # Opponent do draw
                        state = 5

                    self._gui.set_message(self._game.message)
                    matrix = self._game.grid.table
                    self._gui.send_state_matrix(matrix)

                # Me play
                if state < 4:
                    state = -1
                while state <= 2 and self._gui.is_alive():
                    played_cell = self._gui.get_played_cell()
                    if played_cell is not None:  # None if the windows is closed by user
                        state = self._me.play(played_cell)  # return -1 for invalid, 0 for valid, 1 for defeat, 2 for victory
                        self._gui.set_message(self._game.message)

                if self._gui.is_alive() and state <= 5:
                    output = self._myClient.play(played_cell)
                    if not output:  # Happens if server is disconnected
                        state = 7

                    # Update GUI
                    matrix = self._game.grid.table
                    self._gui.send_state_matrix(matrix)

                if state <= 3:
                    played_cell = self._myClient.wait_the_other_to_play(self._gui)

                print(state)

        return int(state)

    def _get_gui(self):
        return self._gui

    gui = property(_get_gui)

