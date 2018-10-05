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
        self.name = name
        self.address = address
        self.port = port
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.matrixSize = (3,3,3)
        self.playerId = None

    def connect(self):
        self.connection.connect((self.address, self.port))
        print("Client " + self.name + " is joining server...")
        self.connection.send(b"JOIN")
        received_message = "DENIED"
        while(received_message == "DENIED"):
            try:
                received_message = self.connection.recv(1024).decode()
                self.playerId = int(received_message)
            except Exception as e:
                print(e)
        print("Client " + self.name + " is connected to server with ID : "+str(self.playerId))

    def send_matrix(self, matrix):
        matrix = np.array(matrix)
        shape = matrix.shape
        if shape == self.matrixSize:
            command = "MATRIX/"+str(self.matrixSize[0])+"/"+str(self.matrixSize[1])+"/"+str(self.matrixSize[2])+"/"
            command = command.encode()

            for i in range(self.matrixSize[0]):
                for j in range(self.matrixSize[1]):
                    for k in range(self.matrixSize[2]):
                        command += str(matrix[i][j][k]).encode()
            print(command)
        else:
            raise Exception("Matrix size is wrong")

    def close_client(self):
        self.connexion_avec_serveur.send(b"QUIT")

    def play(self):
        if self.playerId == 0:




if __name__ == '__main__':
    gabriel = Client("Gabriel", 'localhost', 12800)
    gabriel.connect()

    sylvestre = Client("Sylvestre", 'localhost', 12800)
    sylvestre.connect()

    time.sleep(1)
    gabriel.send_matrix([[[0,0,0], [0,0,0], [0,0,0]], [[0,0,0], [0,0,0], [0,0,0]], [[0,0,0], [0,0,0], [0,0,0]]])