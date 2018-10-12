from tkinter import *
import client

import gamesession
import server
import tkinter.simpledialog


class Menu(Frame):
    def __init__(self, window, **kwargs):
        self._window = window
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
        server1 = server.Server(12800)
        server1.start()

        # Create Client
        client1 = client.Client(name, 'localhost', 12800)
        client1.connect()

        self.play(client1, name)

    def join_server(self):
        name = tkinter.simpledialog.askstring("Name", "What is your name ?")
        address = tkinter.simpledialog.askstring("Address", "What is the address ? ")

        # Creat client, connect to server, and get grid dimension and size.

        client1 = client.Client(name, address, 12800)
        client1.connect()

        self.play(client1, name)

    def play(self, client1, name):
        gamesession.GameSession(client1, name).start_playing()
