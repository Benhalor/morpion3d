from tkinter import *
import client

import gamesession
import server
import tkinter.simpledialog
import socket

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
        self._debugMode = True

    def create_server(self):

        if not self._debugMode:
            self._name = tkinter.simpledialog.askstring("Name", "What is your name ?")
        else:
            self._name = "gabriel"

        dimension = 3

        size = 0
        while size < 3:
            if not self._debugMode:
                size = tkinter.simpledialog.askinteger("Size", "What is the size ? (>2)")
            else:
                size = 3

        # Get and show user IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except:
            IP = '127.0.0.1'
        finally:
            s.close()




        # Create server
        self._playerServer = server.Server(12800, dimension, size, "SERVER")
        self._playerServer.start()

        # Create Client
        self._playerClient = client.Client(self._name, 'localhost', 12800)
        self._playerClient.connect()

        print(IP)
        tkinter.messagebox.showinfo("IP", "L'ip est : "+str(IP))

        self.play(self._playerClient, self._name)



    def join_server(self):
        if not self._debugMode:
            self._name = tkinter.simpledialog.askstring("Name", "What is your name ?")
        else:
            self._name = "Sylvestre"

        validity = False
        while not validity:
            if not self._debugMode:
                address = tkinter.simpledialog.askstring("Address", "What is the address ? ")
            else:
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

            answer = False
            if exit_code <= 6:
                answer = tkinter.messagebox.askyesno("Question", "Do you want to play again?")
            session.gui.stop()

            print(answer)

            # Client part
            if answer:
                state = self._playerClient.replay()  # state = True if Other player wants to replay. False otherwise
                print("replay state "+str(state))
                if not state:
                    boolContinue = False
            else:
                #self._playerClient.stop()
                boolContinue = False

            # Server part, only if the player is the one who has started the server
            if self._playerServer is not None:
                if answer and state:
                    pass
                else:
                    print("Stop server")
                    self._playerServer.stop()
                    self._playerServer = None



        self._playerClient.disconnect()
        self._playerClient = None
        self._window.destroy()
