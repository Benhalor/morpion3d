#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 10:09:31 2018

@author: gabriel
"""

from communicator import Communicator
import numpy as np
import time


class Client(Communicator):
    def __init__(self, name, address, port):
        Communicator.__init__(self, name, port)
        self._address = address
        self._connection.settimeout(1.0)
        self._playerId = None
        self._connected = False

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

        try:
            message = self.read_message(self._connection)
        except TimeoutError:
            print("Other didnt replay within 60s")
            message = "STOP"
        except Exception as e:
            print(e)

        if "OK" in message:
            print("Other player accept to replay")
            return True
        elif "STOP" in message:
            print("Other player stopped")
            return False
        else:
            print("message answer problem "+message)

    def play(self, playedCell):
        self.send_played_cell(playedCell, self._connection)
        print("Send played cell")
        print(playedCell)
        # Wait for confirmation from server
        self._connection.settimeout(5.0)
        received_message = self._connection.recv(1024).decode()
        print("----------"+received_message)
        return received_message == "OK"

    def wait_the_other_to_play(self, gui):
        # Example : CELL/1/1/0
        print(self._name+" is waiting for the other to play")
        received_message = self.wait_message("CELL", gui)
        return self.read_played_cell(received_message)

    def wait_first_cell(self, gui):
        # Server should send START/0 if first player or START/1 if second player
        received_message = self.wait_message("START", gui)
        first = int(received_message.split("/")[-1])
        return first == 0

    def wait_message(self, message_to_wait, gui):
        self._connection.settimeout(1.0)
        received_message = "WAIT"
        while not message_to_wait in received_message and gui.isAlive():
            try:
                received_message = self._connection.recv(1024).decode()
            except Exception as e:
                pass
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



