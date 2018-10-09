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
        self.matrixSize = [3,3]
        self.playerId = None
        self.matrix = np.zeros(self.matrixSize)

    def connect(self):
        self.connection.connect((self.address, self.port))
        print("Client " + self.name + " is joining server...")
        received_message = "DENIED"
        while(received_message == "DENIED"):
            try:
                received_message = self.connection.recv(1024).decode()
                dimension = len(self.matrixSize)
                if dimension == 3:
                    self.connection.send( (str(self.matrixSize[0]) +"/"+str(self.matrixSize[1]) +"/"+str(self.matrixSize[2])).encode() )
                elif dimension == 2:
                    self.connection.send((str(self.matrixSize[0]) + "/" + str(self.matrixSize[1])).encode())
                self.playerId = int(received_message)
            except Exception as e:
                print(e)
        print("Client " + self.name + " is connected to server with ID : "+str(self.playerId))


    def read_matrix(self, string):
        matrix = np.zeros(self.matrixSize)
        dimension = len(self.matrixSize)
        if  dimension == 2:
            count = 0
            for i in range(self.matrixSize[0]):
                for j in range(self.matrixSize[1]):
                    matrix[i,j] = int(string[count])
                    count += 1

        elif dimension == 3:
            count = 0
            for i in range(self.matrixSize[0]):
                for j in range(self.matrixSize[1]):
                    for k in range(self.matrixSize[2]):
                        matrix[i,j,k] = int(string[count])
                        count +=1
        else:
            raise Exception("Dimension is not supported")
        return matrix

    def send_played_cell(self, played_cell):
        if len(played_cell)==2:
            self.connection.send(("CELL/"+str(played_cell[0])+"/"+str(played_cell[1])).encode())
        elif len(played_cell)==3:
            self.connection.send(("CELL/" + str(played_cell[0]) + "/" + str(played_cell[1])+ "/" + str(played_cell[2])).encode())

    def close_client(self):
        self.connexion_avec_serveur.send(b"QUIT")

    def should_I_play(self):
        """Use only for the determine who is the first player"""
        if self.playerId == 0:
            return True
        else:
            return False

    def play(self, played_cell):
        self.send_played_cell(played_cell)
        print("Send played cell")
        print(played_cell)
        #returns the matrix updated on the server
        return self.read_matrix(self.connection.recv(1024).decode().split("/")[-1])

    def wait_the_other_to_play(self):
        received_message = "WAIT"
        print(self.name+" is waiting for the other to play")
        while ("MATRIX" not in received_message):
            try:
                received_message = self.connection.recv(1024).decode()
            except Exception as e:
                print(e)
        return self.read_matrix(received_message.split("/")[-1])



if __name__ == '__main__':
    gabriel = Client("Gabriel", 'localhost', 12800)
    gabriel.connect()

    sylvestre = Client("Sylvestre", 'localhost', 12800)
    sylvestre.connect()


    gabriel.wait_the_other_to_play()


    while(True):
        # The game engine returns the matrix A with the new play
        A = [[[0,0,0], [0,5,0], [0,0,0]], [[0,0,0], [0,3,0], [0,0,0]], [[0,0,0], [0,0,0], [7,0,0]]]
        A = [ [0,1,0],[0,0,1],[0,0,0] ]
        print(gabriel.play([1,2]))
        A = gabriel.wait_the_other_to_play()

    time.sleep(1)
    gabriel.send_matrix([[[0,0,0], [0,0,0], [0,0,0]], [[0,0,0], [0,0,0], [0,0,0]], [[0,0,0], [0,0,0], [0,0,0]]])