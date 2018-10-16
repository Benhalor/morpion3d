#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 10:09:31 2018

@author: gabriel
"""

import socket
import numpy as np
import time

class Client():
    def __init__(self, name, address, port):
        self._name = name
        self._address = address
        self._port = port
        self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connection.settimeout(1.0)
        self._matrixSize = None
        self._playerId = None
        self._dimension = None

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
        return True


    def send_played_cell(self, played_cell):
        command = ""
        if len(played_cell)==2:
            command = ("CELL/"+str(played_cell[0])+"/"+str(played_cell[1])).encode()

        elif len(played_cell)==3:
            command = ("CELL/" + str(played_cell[0]) + "/" + str(played_cell[1])+ "/" + str(played_cell[2])).encode()

        try:
            self._connection.send(command)
        except ConnectionAbortedError:
            return False
        else:
            return True



    def should_I_play(self):
        """Use only for the determine who is the first player"""
        if self._playerId == 0:
            return True
        else:
            return False

    def play(self, played_cell):
        self.send_played_cell(played_cell)
        print("Send played cell")
        print(played_cell)
        # Wait for confirmation from server
        received_message = self._connection.recv(1024).decode()
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

    matrixSize = property(_get_matrixSize)
    playerId = property(_get_playerId)
    dimension = property(_get_dimension)
