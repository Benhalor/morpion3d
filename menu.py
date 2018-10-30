#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tkinter import *
import client

import gamesession
import server
import tkinter.simpledialog
import socket


class Menu(Frame):
    """ Menu
    A windows menu for selecting the parameter for playing.
    If you click on "Join Server" it tries to join the server on the given address
    If you click on "Create Server" a server will be created on your computer it joins the server on the localhost address

    Usage example:

    mainMenu = menu.Menu(window)
    mainMenu.mainloop()

    """

    def __init__(self, window, **kwargs):
        self.__window = window
        Frame.__init__(self, self.__window, width=768, height=576, **kwargs)
        self.pack(fill=BOTH)

        self.__labelName = Label(self, text="Name: ")
        self.__labelName.grid(row=0, column=0)

        self.__entryName = Entry(self)
        self.__entryName.insert(0, "Gabriel")
        self.__entryName.grid(row=0, column=1)

        self.__labelSize = Label(self, text="Size: ")
        self.__labelSize.grid(row=1, column=0)

        self.__entrySize = Entry(self)
        self.__entrySize.insert(0, "3")
        self.__entrySize.grid(row=1, column=1)

        self.__labelAddress = Label(self, text="Join adress: ")
        self.__labelAddress.grid(row=2, column=0)

        self.__entryAddress = Entry(self)
        self.__entryAddress.insert(0, "localhost")
        self.__entryAddress.grid(row=2, column=1)

        self.__createServer = Button(self, text="Create Server", command=self.__create_server)
        self.__createServer.grid(row=3, column=0)

        self.__joinServer = Button(self, text="Join Server", command=self.__join_server)
        self.__joinServer.grid(row=3, column=1)

        self.__name = None
        self.__playerServer = None
        self.__playerClient = None
        self.__debugMode = True  # Used for fast debug mode in local : doesnt ask the user to choose name/adress

    def __create_server(self):

        self.__name = self.__entryName.get()
        if len(self.__name) > 30:
            tkinter.messagebox.showerror("ValueError", "Name is too long (max 30)")
            return 0

        dimension = 3

        size = 0
        try:
            size = int(self.__entrySize.get())
            if size < 3 or size > 9:
                tkinter.messagebox.showerror("ValueError", "Size should be between 3 and 9")
                return 0
        except ValueError:
            tkinter.messagebox.showerror("ValueError", "Size should be an int")
            return 0


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
        try:
            self.__playerServer = server.Server(12800, dimension, size, "SERVER")
        except OSError:
            tkinter.messagebox.showerror("OSError", "Unable to start server."
                                                    "Port is blocked by firewall or another server is already running")
            return 0
        self.__playerServer.start()

        # Create Client
        self.__playerClient = client.Client(self.__name, 'localhost', 12800)
        self.__playerClient.connect()

        # Show IP to help the other to connect
        print(IP)
        tkinter.messagebox.showinfo("IP", "Your IP is : " + str(IP))

        self.__play(self.__playerClient, self.__name)

    def __join_server(self):
        self.__name = self.__entryName.get()
        if len(self.__name) > 30:
            tkinter.messagebox.showerror("ValueError", "Name is too long (max 30)")
            return 0

        validity = False
        address = self.__entryAddress.get()

        # Create client, connect to server, and get grid dimension and size.
        try:
            self.__playerClient = client.Client(self.__name, address, 12800)
            validity = self.__playerClient.connect()
        except:  # Excepts when server is not reachable
            validity = False

        if not validity:
            tkinter.messagebox.showerror("Error", "Unable to connect to " + address)
            return 0

        self.__play(self.__playerClient, self.__name)

    def __play(self, playerClient, name):

        # hide the tkinter windows. Mandatory to get tkinter tkinter messageboxes in foreground
        self.__window.withdraw()

        #  Loop for playing many games
        boolContinue = True
        while boolContinue:
            # Play a game and get the exit code
            session = gamesession.GameSession(playerClient, name)
            exit_code = session.start_playing()

            if exit_code == 4:
                tkinter.messagebox.showinfo("INFO", "Victory " + self.__name)
            if exit_code == 5:
                tkinter.messagebox.showinfo("INFO", "It's a draw")
            if exit_code == 6:
                tkinter.messagebox.showinfo("INFO", "Defeat " + self.__name)
            if exit_code == 7:
                tkinter.messagebox.showerror("Error", "Other disconnected")
            elif exit_code == 8:
                tkinter.messagebox.showerror("Error", "Server or other disconnected")

            answer = False
            if exit_code <= 6:
                answer = tkinter.messagebox.askyesno("Question", "Do you want to play again?")
            session.gui.stop()
            session.gui.join()

            print(answer)

            # Client part
            if answer:
                state = self.__playerClient.replay()  # state = True if Other player wants to replay. False otherwise
                print("replay state " + str(state))
                if not state:
                    boolContinue = False
                    tkinter.messagebox.showerror("Error", "Other doesnt want to replay")
            else:
                # self._playerClient.stop()
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
