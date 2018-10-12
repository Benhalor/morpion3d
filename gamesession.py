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
        self._game.start(self._myClient.playerId)

        # GUI
        self._gui = guiMainWindow.MainWindow(self._matrixSize)
        self._gui.start()

    def start_playing(self):
        state = 0
        while state != 1 and state != 2:

            # Opponent play
            played_cell = self._myClient.wait_the_other_to_play()
            if -1 not in played_cell:  # -1 if nothing to update (normally happens only if you at the first cell)
                self._opponent.play(played_cell)
                self._gui.set_message(self._game.message)
                matrix = self._game.grid.table
                self._gui.send_state_matrix(matrix)

            # Me play
            played_cell = self._gui.get_played_cell()

            state = -1
            while state == -1:
                state = self._me.play(played_cell)  # return -1 for invalid, 0 for valid, 1 for defeat, 2 for victory
                self._gui.set_message(self._game.message)
            self._myClient.play(played_cell)

            # Update GUI
            matrix = self._game.grid.table
            self._gui.send_state_matrix(matrix)