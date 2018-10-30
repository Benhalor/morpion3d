#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from communicator import Communicator
from morpionExceptions import *
import guiMainWindow


class Client(Communicator):
    def __init__(self, name, address, port):
        Communicator.__init__(self, name, port)
        self.__address = address
        self._connection.settimeout(1.0)
        self.__playerId = None
        self.__connected = False
        self.__gui = None

    def __repr__(self):
        if self._connected:
            return "Client : "+str(self._name)+" is connected on address : " + str(self.__address)+" with port : " + \
                   str(self._port)
        else:
            return "Client : "+str(self._name)+" is not connected"

    def connect(self):
        # The connect method may raise an error is server is unreachable. This error is catch in the Menu class
        self._connection.connect((self.__address, self._port))
        print("Client " + self._name + " is joining server...")

        received_message = ""
        while(received_message == ""):
            try:
                # Expected message from server : "id/dimension/size"
                received_message = self._connection.recv(1024).decode()
                split = received_message.split("/")
                self.__playerId = int(split[0])
                self._dimension = int(split[1])
                self._matrixSize = int(split[2])
            except Exception as e:
                print(e)
        print("Client " + self._name + " is connected to server with ID : "+str(self.__playerId))
        self.__connected = True
        return True

    def disconnect(self):
        if self.__connected:
            self._connection.close()

    def replay(self):

        # Send reset message to sever
        self._send_message("RESET", self._connection)
        self._connection.settimeout(60.0)

        # The server waits for the other to reply and send you "OK" if the other wants to replay, or "STOP" otherwise.
        received_message = self.__wait_message(["STOP", "OK", "ERROR"])

        if "OK" in received_message:
            print("Other player accept to replay")
            return True
        elif "STOP" in received_message:
            print("Other player stopped")
            return False

    def play(self, playedCell):
        # Send the played cell to server
        self._send_played_cell(playedCell, self._connection)
        print(self._name + " send played cell")
        print(playedCell)

        # Wait for confirmation "OK" from server
        self._connection.settimeout(5.0)
        received_message = self.__wait_message(["OK", "STOP", "ERROR"], checkGui=True)
        return received_message == "OK"

    def wait_the_other_to_play(self, gui):
        """ Wait the cell of the other player from the server"""
        print(self._name+" is waiting for the other to play")

        #Expected message : "CELL/1/2/" or "STOP" if the other want to stop
        received_message = self.__wait_message(["CELL", "STOP", "ERROR"], checkGui= True)

        # If server is disconnected, raise ServerError
        if self._error is None:
            return self._read_played_cell(received_message)
        else:
            raise ServerError()

    def wait_for_start(self, gui):
        """ Wait the start message from server at beginning"""
        print(self._name + " Wait first cell")

        # Expected message : START/0 if first player or START/1 if second player
        received_message = self.__wait_message(["START", "STOP", "ERROR"], checkGui= True)
        first = int(received_message.split("/")[-1])
        if self._error is None:
            return first == 0
        else:
            raise ServerError()

    def __wait_message(self, messages_to_wait, checkGui = False):
        """ Wait one of the string in messages_to_wait and check that the gui is not stopped"""
        self._connection.settimeout(1.0)
        received_message = "WAIT"

        while not Communicator._is_in(messages_to_wait, received_message) and (not checkGui or self.__gui.isAlive()):
            try:
                received_message = self._read_message(self._connection)
                print(received_message)
            except Exception:
                pass

        if not self.__gui.isAlive() and checkGui:
            raise GuiNotAliveError()

        return received_message

    def stop(self):
        """Send "STOP" message to server"""
        self._send_message("STOP", self._connection)

    def __get_matrixSize(self):
        return self._matrixSize
    matrixSize = property(__get_matrixSize)

    def __get_playerId(self):
        return self.__playerId
    playerId = property(__get_playerId)

    def __get_dimension(self):
        return self._dimension
    dimension = property(__get_dimension)

    def __get_gui(self):
        return self.__gui

    def __set_gui(self, gui):
        if isinstance(gui, guiMainWindow.MainWindow):
            self.__gui = gui
        else:
            raise NotGuiMainWindowsInstance
    gui = property(__get_gui, __set_gui)



