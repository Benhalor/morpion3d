from tkinter import *
import client

import gamesession
import server
import tkinter.simpledialog


class Menu(Frame):
    def __init__(self, window, **kwargs):
        self._window = window
        self._playerServer = None
        Frame.__init__(self, window, width=768, height=576, **kwargs)
        self.pack(fill=BOTH)

        self._createServer = Button(self, text="Create Server", command=self.create_server)
        self._createServer.pack(side="left")

        self._joinServer = Button(self, text="Join Server", command=self.join_server)
        self._joinServer.pack(side="right")

    def create_server(self):
        name = tkinter.simpledialog.askstring("Name", "What is your name ?")

        dimension = 0
        while dimension > 3 or dimension < 2:
            dimension = tkinter.simpledialog.askinteger("Dimension", "What is the dimension ? (2 or 3)")

        size = 0
        while size < 3:
            size = tkinter.simpledialog.askinteger("Size", "What is the size ? (>2)")

        # Create server
        self._playerServer = server.Server(12800, dimension)
        self._playerServer.start()

        # Create Client
        playerClient = client.Client(name, 'localhost', 12800)
        playerClient.connect()

        self.play(playerClient, name)

    def join_server(self):
        name = tkinter.simpledialog.askstring("Name", "What is your name ?")

        validity = False
        while not validity:
            address = tkinter.simpledialog.askstring("Address", "What is the address ? ")
            # Create client, connect to server, and get grid dimension and size.
            try:
                playerClient = client.Client(name, address, 12800)
                validity = playerClient.connect()
            except:
                tkinter.messagebox.showerror("Error", "Unable to connect")

        self.play(playerClient, name)

    def play(self, playerClient, name):
        gamesession.GameSession(playerClient, name).start_playing()
        print("joined")
        if self._playerServer is not None:
            print("Stop server")
            self._playerServer.stop()
            self._playerServer = None
