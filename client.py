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


    def send_played_cell(self, played_cell):
        if len(played_cell)==2:
            self._connection.send(("CELL/"+str(played_cell[0])+"/"+str(played_cell[1])).encode())
        elif len(played_cell)==3:
            self._connection.send(("CELL/" + str(played_cell[0]) + "/" + str(played_cell[1])+ "/" + str(played_cell[2])).encode())

    def close_client(self):
        self.connexion_avec_serveur.send(b"QUIT")

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
        #returns the matrix updated on the server
        received_message = self._connection.recv(1024).decode()
        return received_message == "OK"

    def read_played_cell(self, received_message):
        #CELL/2/2
        print(received_message)
        if self._dimension == 2:
            split = received_message.split("/")
            cell = [int(split[1]), int(split[2])]
        if self._dimension == 3:
            split = received_message.split("/")
            cell = [int(split[1]), int(split[2]), int(split[3])]
        return cell

    def wait_the_other_to_play(self):
        received_message = "WAIT"
        print(self._name+" is waiting for the other to play")
        while ("CELL" not in received_message):
            try:
                received_message = self._connection.recv(1024).decode()
            except Exception as e:
                print(e)
        return self.read_played_cell(received_message)

    matrixSize = property(_get_matrixSize)
    playerId = property(_get_playerId)
    dimension = property(_get_dimension)
