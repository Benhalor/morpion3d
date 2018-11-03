class ServerError(Exception):
    def __init__(self):
        self.__message = "The server returns an error"


class GuiNotAliveError(Exception):
    def __init__(self):
        self.__message = "Gui not alive"


class NotGuiMainWindowsInstance(Exception):
    def __init__(self):
        self.__message = " Not an instance of GUI"

class GamePlayerError(Exception):
    def __init__(self):
        self.__message = "Player was not recognized by the game"
        
class GameTurnError(Exception):
    def __init__(self):
        self.__message = "It is not the player's turn"