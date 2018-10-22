#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 10:09:31 2018

@author: gabriel
"""

import socket
import numpy as np
import time


class Client:
    def __init__(self, name, address, port):
        self._name = name
        self._address = address
        self._port = port
        self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connection.settimeout(1.0)
        self._matrixSize = None
        self._playerId = None
        self._dimension = None
        self._connected = False

    def _get_matrixSize(self):
        return self._matrixSize

    def _get_playerId(self):
        return self._playerId

    def _get_dimension(self):
        return self._dimension

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

    def send_played_cell(self, played_cell):
        command = ""
        if len(played_cell)==2:
            command = ("CELL/"+str(played_cell[0])+"/"+str(played_cell[1]))

        elif len(played_cell)==3:
            command = ("CELL/" + str(played_cell[0]) + "/" + str(played_cell[1])+ "/" + str(played_cell[2]))

        try:
            self.send_message(command, self._connection)
        except (ConnectionAbortedError, ConnectionResetError):
            return False
        else:
            return True

    def send_message(self, message, connection):
        print("CLIENT " + self._name+" SEND: " + message)
        connection.send(message.encode())

    def play(self, played_cell):
        self.send_played_cell(played_cell)
        print("Send played cell")
        print(played_cell)
        # Wait for confirmation from server
        self._connection.settimeout(5.0)
        received_message = self._connection.recv(1024).decode()
        print("----------"+received_message)
        return received_message == "OK"

    def read_played_cell(self, received_message):
        #CELL/2/2
        print("RECEIVED MESSAGE FOR PLAYER "+str(self._playerId)+" : "+str(received_message))
        split = received_message.split("/")
        if len(split) == self._dimension +1:
            if self._dimension == 2:
                cell = [int(split[1]), int(split[2])]
            if self._dimension == 3:
                cell = [int(split[1]), int(split[2]), int(split[3])]
        else:
            cell = received_message
        return cell

    def read_message(self, connection):
        try:
            message = connection.recv(1024).decode()
            return message
        except (ConnectionAbortedError, ConnectionResetError):
            return "ERROR"


    def wait_the_other_to_play(self, gui):
        received_message = "WAIT"
        self._connection.settimeout(1.0)
        print(self._name+" is waiting for the other to play")
        while "WAIT" in received_message and gui.isAlive():
            try:
                received_message = self._connection.recv(1024).decode()
            except Exception as e:
                pass
                #print(e)
        if not gui.isAlive():
            print("Connection stopped on isAlive")
            return "STOP"
        return self.read_played_cell(received_message)

    def wait_first_cell(self, gui):
        received_message = "WAIT"
        self._connection.settimeout(1.0)
        print(self._name + " is waiting for the first cell")
        # Server should send START/0 if first player or START/1 if second player
        while not "START" in received_message and gui.isAlive():
            try:
                received_message = self._connection.recv(1024).decode()
            except Exception as e:
                pass
        if not gui.isAlive():
            print("Connection stopped on isAlive")
            return "STOP"
        first = int(received_message.split("/")[-1])
        return first == 0

    def stop(self):
        self.send_message("STOP", self._connection)

    def __repr__(self):
        if self._connected:
            return "Client : "+str(self._name)+" is connected on address : " + str(self._address)+" with port : " + \
                   str(self._port)
        else:
            return "Client : "+str(self._name)+" is not connected"

    matrixSize = property(_get_matrixSize)
    playerId = property(_get_playerId)
    dimension = property(_get_dimension)
