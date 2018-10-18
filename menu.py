from tkinter import *
import client

import gamesession
import server
import tkinter.simpledialog


class Menu(Frame):
    def __init__(self, window, **kwargs):
        self._window = window
        Frame.__init__(self, self._window, width=768, height=576, **kwargs)
        self.pack(fill=BOTH)

        self._createServer = Button(self, text="Create Server", command=self.create_server)
        self._createServer.pack(side="left")

        self._joinServer = Button(self, text="Join Server", command=self.join_server)
        self._joinServer.pack(side="right")

        self._name = None
        self._playerServer = None
        self._playerClient = None

    def create_server(self):
        # self._name = tkinter.simpledialog.askstring("Name", "What is your name ?")
        self._name = "gabriel"

        dimension = 0
        while dimension > 3 or dimension < 2:
            #dimension = tkinter.simpledialog.askinteger("Dimension", "What is the dimension ? (2 or 3)")
            dimension = 2

        size = 0
        while size < 3:
            #size = tkinter.simpledialog.askinteger("Size", "What is the size ? (>2)")
            size = 3

        # Create server
        self._playerServer = server.Server(12800, dimension, size)
        self._playerServer.start()

        # Create Client
        self._playerClient = client.Client(self._name, 'localhost', 12800)
        self._playerClient.connect()

        self.play(self._playerClient, self._name)

    def join_server(self):
        # self._name = tkinter.simpledialog.askstring("Name", "What is your name ?")
        self._name = "Sylvestre"

        validity = False
        while not validity:
            #address = tkinter.simpledialog.askstring("Address", "What is the address ? ")
            address = "localhost"
            # Create client, connect to server, and get grid dimension and size.
            try:
                self._playerClient = client.Client(self._name, address, 12800)
                validity = self._playerClient.connect()
            except:
                tkinter.messagebox.showerror("Error", "Unable to connect")

        self.play(self._playerClient, self._name)

    def play(self, playerClient, name):
        boolContinue = True
        while boolContinue:
            session = gamesession.GameSession(playerClient, name)
            exit_code = session.start_playing()

            self._window.update()

            if exit_code == 4:
                print("victoire")
                tkinter.messagebox.showinfo("INFO", "Victory "+ self._name)
            if exit_code == 5:
                tkinter.messagebox.showinfo("INFO", "It's a draw")
            if exit_code == 6:
                tkinter.messagebox.showinfo("INFO", "Defeat "+ self._name)
            if exit_code == 7:
                tkinter.messagebox.showerror("Error", "Other disconnected")
            elif exit_code == 8:
                tkinter.messagebox.showerror("Error", "Server disconnected")

            answer = tkinter.messagebox.askyesno("Question", "Do you want to play again?")
            session.gui.stop()

            print(answer)

            # Server part, only if the player is the one who has started the server
            if self._playerServer is not None:
                if answer:
                    pass
                else:
                    print("Stop server")
                    self._playerServer.stop()
                    self._playerServer = None

            # Client part
            if answer:
                pass
                self._playerClient.replay()
                # wait other to replay
            else:
                self._playerClient.disconnect()
                self._playerClient = None
                boolContinue = False
