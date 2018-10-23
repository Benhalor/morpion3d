

class ServerError(Exception):
    def __init__(self):
        self.message = "The server returns an error"


class GuiNotAliveError(Exception):
    def __init__(self):
        self.message = "Gui not alive"