#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 10:09:31 2018

@author: gabriel
"""

from communicator import Communicator
from morpionExceptions import ServerError, GuiNotAliveError
import traceback
import socket
import numpy as np
import time


class Client(Communicator):
    def __init__(self, name, address, port):
        Communicator.__init__(self, name, port)
        self._address = address
        self._connection.settimeout(1.0)
        self._playerId = None
        self._connected = False
        self._gui = None

    def __repr__(self):
        if self._connected:
            return "Client : "+str(self._name)+" is connected on address : " + str(self._address)+" with port : " + \
                   str(self._port)
        else:
            return "Client : "+str(self._name)+" is not connected"

    def connect(self):
        self._connection.connect((self._address, self._port))
        print("Client " + self._name + " is joining server...")
        received_message = "DENIED"
        while(received_message == "DENIED"):
            try:
                received_message = self._connection.recv(1024).decode()
                split = received_message.split("/")
                self._playerId = int(split[0])
                self._dimension = int(split[1])
                self._matrixSize = int(split[2])
            except Exception as e:
                print(e)
        print("Client " + self._name + " is connected to server with ID : "+str(self._playerId))
        self._connected = True
        return True

    def disconnect(self):
        if self._connected:
            self._connection.close()

    def replay(self):
        self.send_message("RESET", self._connection)
        self._connection.settimeout(60.0)

        received_message = self.wait_message(["STOP", "OK", "ERROR"])

        if "OK" in received_message:
            print("Other player accept to replay")
            return True
        elif "STOP" in received_message:
            print("Other player stopped")
            return False

    def play(self, playedCell):
        self.send_played_cell(playedCell, self._connection)
        print(self._name + " send played cell")
        print(playedCell)

        # Wait for confirmation from server
        self._connection.settimeout(5.0)
        received_message = self.read_message(self._connection)
        print("----------"+received_message)
        return received_message == "OK"

    def wait_the_other_to_play(self, gui):
        # Example : CELL/1/1/0
        print(self._name+" is waiting for the other to play")
        received_message = self.wait_message(["CELL", "STOP", "ERROR"], checkGui= True)
        if self._error is None:
            return self.read_played_cell(received_message)
        else:
            raise ServerError()

    def wait_first_cell(self, gui):
        # Server should send START/0 if first player or START/1 if second player
        print(self._name + " Wait first cell")
        received_message = self.wait_message(["START", "STOP", "ERROR"], checkGui= True)
        first = int(received_message.split("/")[-1])
        if self._error is None:
            return first == 0
        else:
            raise ServerError()

    def wait_message(self, messages_to_wait, checkGui = False):
        self._connection.settimeout(1.0)
        received_message = "WAIT"

        while not Communicator.is_in(messages_to_wait, received_message) and (not checkGui or self._gui.isAlive()):
            try:

                received_message = self.read_message(self._connection)
                print("WAIT ESSda")
                print(received_message)
            except Exception:
                pass

        if not self._gui.isAlive() and checkGui:
            raise GuiNotAliveError()

        return received_message

    def stop(self):
        self.send_message("STOP", self._connection)

    def _get_matrixSize(self):
        return self._matrixSize
    matrixSize = property(_get_matrixSize)

    def _get_playerId(self):
        return self._playerId
    playerId = property(_get_playerId)

    def _get_dimension(self):
        return self._dimension
    dimension = property(_get_dimension)

    def _get_gui(self):
        return self._gui
    def _set_gui(self, gui):
        self._gui = gui
    gui = property(_get_gui, _set_gui)



