class ServerError(Exception):
    def __init__(self):
        self.__message = "The server returns an error"


class GuiNotAliveError(Exception):
    def __init__(self):
        self.__message = "Gui not alive"


class NotGuiMainWindowsInstance(Exception):
    def __init__(self):
        self.__message = " Not an instance of GUI"

class GameError(Exception):
    def __init__(self):
        self.__message = "Something went wrong with the game"