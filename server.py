#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 10:09:31 2018

@author: gabriel
"""

#python PycharmProjects/morpion3d/server.py
import socket
import numpy as np
from threading import Thread

class Server(Thread):
    def __init__(self, port):
        Thread.__init__(self)
        self.numberOfPlayers = 2
        self.port = port
        self.listOfConnections = []
        self.listOfInfoConnections = []
        self.listOfPlayerId = []
        self.idCounter = 1 #begins to 1 because 0 id means the cell is not yet played
        self.matrixSize = None
        self.matrix = []
        print("Server started")

    def send_played_cell(self, played_cell):
        if len(played_cell)==2:
            self.connection.send(("CELL/"+str(played_cell[0])+"/"+str(played_cell[1])).encode())
        elif len(played_cell)==3:
            self.connection.send(("CELL/" + str(played_cell[0]) + "/" + str(played_cell[1])+ "/" + str(played_cell[2])).encode())


    def connect_clients (self):
        print("waiting for clients to connect")
        self.main_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.main_connection.bind(('', self.port))
        self.main_connection.listen(5)


        for i in range(self.numberOfPlayers):
            tempConnection , tempsInfoConnection = self.main_connection.accept()
            tempConnection.send(str(self.idCounter).encode())
            received_message = tempConnection.recv(1024).decode()

            #read dimension of matrix and check that all players want the same
            if self.matrixSize == None:
                self.matrixSize = [int(element) for element in received_message.split("/")]
                self.matrix = np.zeros(self.matrixSize)
            else:
                if self.matrixSize != [int(element) for element in received_message.split("/")]:
                    raise Exception("Players doesnt want the same dimension...")
                else:
                    print("Dimension checked: " + str(self.matrixSize))

            print((bytearray(self.idCounter)))
            self.listOfPlayerId.append(self.idCounter)
            self.listOfConnections.append(tempConnection)
            self.listOfInfoConnections.append(tempsInfoConnection)
            self.idCounter += 1
            print(tempsInfoConnection)
        print("Clients connected")

    def send_played_cell(self, played_cell, connection):
        if len(played_cell)==2:
            connection.send(("CELL/"+str(played_cell[0])+"/"+str(played_cell[1])).encode())
        elif len(played_cell)==3:
            connection.send(("CELL/" + str(played_cell[0]) + "/" + str(played_cell[1])+ "/" + str(played_cell[2])).encode())

    def send_matrix(self,connection, matrix):
        print("Sending matrix to client")

        command = "MATRIX/"
        command = command.encode()

        dimension = len(self.matrixSize)
        if dimension == 2:
            for i in range(self.matrixSize[0]):
                for j in range(self.matrixSize[1]):
                    command += str(int(matrix[i][j])).encode()

        elif dimension == 3:
            for i in range(self.matrixSize[0]):
                for j in range(self.matrixSize[1]):
                    for k in range(self.matrixSize[2]):
                        command += str(int(matrix[i][j][k])).encode()
        else:
            raise Exception("Dimension is not supported")
        print(command)
        connection.send(command)

    def run(self):
        received_message = "OK"
        played_cell = [-1, -1]
        while (True):
            for i in range (self.numberOfPlayers):
                self.send_played_cell(played_cell, self.listOfConnections[i])
                received_message = self.listOfConnections[i].recv(1024).decode()
                print("SERVER: "+received_message)
                if "CELL" in received_message:
                    if len(self.matrixSize) == 2:
                        split =received_message.split("/")
                        played_cell = [int(split[1]), int(split[2])]
                        self.matrix[played_cell[0], played_cell[1]] = self.listOfPlayerId[i]
                    if len(self.matrixSize) == 3:
                        split =received_message.split("/")
                        played_cell = [int(split[1]), int(split[2]), int(split[3])]
                        self.matrix[played_cell[0], played_cell[1], played_cell[2]] = self.listOfPlayerId[i]
                    print("SERVER CELL")
                    print(played_cell)
                    self.send_played_cell(played_cell, self.listOfConnections[i])
        print("run")




if __name__ == '__main__':
    server = Server(12800)
    server.connect_clients()
    server.start()