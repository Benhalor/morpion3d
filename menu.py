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
        #name = "gabriel"

        dimension = 0
        while dimension > 3 or dimension < 2:
            dimension = tkinter.simpledialog.askinteger("Dimension", "What is the dimension ? (2 or 3)")
            #dimension = 3

        size = 0
        while size < 3:
            size = tkinter.simpledialog.askinteger("Size", "What is the size ? (>2)")
            #size = 3

        # Create server
        self._playerServer = server.Server(12800, dimension)
        self._playerServer.start()

        # Create Client
        playerClient = client.Client(name, 'localhost', 12800)
        playerClient.connect()

        self.play(playerClient, name)

    def join_server(self):
        name = tkinter.simpledialog.askstring("Name", "What is your name ?")
        #name = "Sylvestre"

        validity = False
        while not validity:
            address = tkinter.simpledialog.askstring("Address", "What is the address ? ")
            #address = "localhost"
            # Create client, connect to server, and get grid dimension and size.
            try:
                playerClient = client.Client(name, address, 12800)
                validity = playerClient.connect()
            except:
                tkinter.messagebox.showerror("Error", "Unable to connect")

        self.play(playerClient, name)

    def play(self, playerClient, name):
        session = gamesession.GameSession(playerClient, name)
        exit_code = session.start_playing()

        if exit_code == 4:
            tkinter.messagebox.showinfo("Error", "Victory")
        if exit_code == 5:
            tkinter.messagebox.showinfo("Error", "Equality")
        if exit_code == 6:
            tkinter.messagebox.showinfo("Error", "Defeat")
        if exit_code == 7:
            tkinter.messagebox.showerror("Error", "Other disconnected")
        elif exit_code == 8:
            tkinter.messagebox.showerror("Error", "Server disconnected")

        session.gui.stop()
        print("joined")
        if self._playerServer is not None:
            print("Stop server")
            self._playerServer.stop()
            self._playerServer = None
