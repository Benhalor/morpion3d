from tkinter import *
import client

import gamesession
import server
import tkinter.simpledialog
import socket

class Menu(Frame):
    def __init__(self, window, **kwargs):
        self.__window = window
        Frame.__init__(self, self.__window, width=768, height=576, **kwargs)
        self.pack(fill=BOTH)

        self.__createServer = Button(self, text="Create Server", command=self.__create_server)
        self.__createServer.pack(side="left")

        self.__joinServer = Button(self, text="Join Server", command=self.__join_server)
        self.__joinServer.pack(side="right")

        self.__name = None
        self.__playerServer = None
        self.__playerClient = None
        self.__debugMode = False  # Used for fast debug mode in local : doesnt ask the user to choose name/adress

    def __create_server(self):

        if not self.__debugMode:
            self.__name = tkinter.simpledialog.askstring("Name", "What is your name ?")
        else:
            self.__name = "gabriel"

        dimension = 3

        size = 0
        while size < 3 or size > 9:
            if not self.__debugMode:
                size = tkinter.simpledialog.askinteger("Size", "What is the size ? (3 <= Size <= 9)")
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
        self.__playerServer = server.Server(12800, dimension, size, "SERVER")
        self.__playerServer.start()

        # Create Client
        self.__playerClient = client.Client(self.__name, 'localhost', 12800)
        self.__playerClient.connect()

        print(IP)
        tkinter.messagebox.showinfo("IP", "L'ip est : "+str(IP))

        self.__play(self.__playerClient, self.__name)

    def __join_server(self):
        if not self.__debugMode:
            self.__name = tkinter.simpledialog.askstring("Name", "What is your name ?")
        else:
            self.__name = "Sylvestre"

        validity = False
        while not validity:
            if not self.__debugMode:
                address = tkinter.simpledialog.askstring("Address", "What is the address ? ")
            else:
                address = "localhost"
            # Create client, connect to server, and get grid dimension and size.
            try:
                self.__playerClient = client.Client(self.__name, address, 12800)
                validity = self.__playerClient.connect()
            except:
                tkinter.messagebox.showerror("Error", "Unable to connect")

        self.__play(self.__playerClient, self.__name)

    def __play(self, playerClient, name):
        boolContinue = True
        while boolContinue:
            session = gamesession.GameSession(playerClient, name)
            exit_code = session.start_playing()

            self.__window.update()

            if exit_code == 4:
                print("victoire")
                tkinter.messagebox.showinfo("INFO", "Victory "+ self.__name)
            if exit_code == 5:
                tkinter.messagebox.showinfo("INFO", "It's a draw")
            if exit_code == 6:
                tkinter.messagebox.showinfo("INFO", "Defeat "+ self.__name)
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
                state = self.__playerClient.replay()  # state = True if Other player wants to replay. False otherwise
                print("replay state "+str(state))
                if not state:
                    boolContinue = False
                    tkinter.messagebox.showerror("Error", "Other doesnt want to replay")
            else:
                #self._playerClient.stop()
                boolContinue = False

            # Server part, only if the player is the one who has started the server
            if self.__playerServer is not None:
                if answer and state:
                    pass
                else:
                    print("Stop server")
                    self.__playerServer.stop()
                    self.__playerServer = None

        self.__playerClient.disconnect()
        self.__playerClient = None
        self.__window.destroy()
