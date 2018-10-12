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
        self._numberOfPlayers = 2
        self._port = port
        self._listOfConnections = []
        self._listOfInfoConnections = []
        self._listOfPlayerId = []
        self._idCounter = 1 #begins to 1 because 0 id means the cell is not yet played
        self._matrixSize = 3 #assume it is a square matrix
        self._dimension = 2
        self._matrix = np.zeros([self._matrixSize for i in range(self._dimension)])
        print("Server started")


    def send_played_cell(self, played_cell):
        if len(played_cell)==2:
            self.connection.send(("CELL/"+str(played_cell[0])+"/"+str(played_cell[1])).encode())
        elif len(played_cell)==3:
            self.connection.send(("CELL/" + str(played_cell[0]) + "/" + str(played_cell[1])+ "/" + str(played_cell[2])).encode())


    def connect_clients (self):
        print("waiting for clients to connect")
        self.main_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.main_connection.bind(('', self._port))
        self.main_connection.listen(5)


        for i in range(self._numberOfPlayers):
            #id/_dimension/size #assume it is a square matrix
            tempConnection , tempsInfoConnection = self.main_connection.accept()
            command = str(self._idCounter)+"/"
            command += str(self._dimension)+ "/"
            command += str(self._matrixSize)

            tempConnection.send(command.encode())
            print((bytearray(self._idCounter)))
            self._listOfPlayerId.append(self._idCounter)
            self._listOfConnections.append(tempConnection)
            self._listOfInfoConnections.append(tempsInfoConnection)
            self._idCounter += 1
            print(tempsInfoConnection)
        print("Clients connected")

    def send_played_cell(self, played_cell, connection):
        if len(played_cell)==2:
            connection.send(("CELL/"+str(played_cell[0])+"/"+str(played_cell[1])).encode())
        elif len(played_cell)==3:
            connection.send(("CELL/" + str(played_cell[0]) + "/" + str(played_cell[1])+ "/" + str(played_cell[2])).encode())


    def run(self):
        self.connect_clients()
        received_message = "OK"
        played_cell = [-1, -1]
        reset = False
        stop = False

        while not stop:
            while not reset and not stop:
                for element in self._listOfPlayerId:
                    i = element - 1
                    self.send_played_cell(played_cell, self._listOfConnections[i])
                    received_message = self._listOfConnections[i].recv(1024).decode()
                    print("SERVER: "+received_message)
                    if "CELL" in received_message:
                        if self._dimension == 2:
                            split =received_message.split("/")
                            played_cell = [int(split[1]), int(split[2])]
                            self._matrix[played_cell[0], played_cell[1]] = self._listOfPlayerId[i]
                        if self._dimension == 3:
                            split =received_message.split("/")
                            played_cell = [int(split[1]), int(split[2]), int(split[3])]
                            self._matrix[played_cell[0], played_cell[1], played_cell[2]] = self._listOfPlayerId[i]
                        print("SERVER CELL")
                        print(played_cell)
                        self._listOfConnections[i].send(b"OK")
                    if "RESET" in received_message:
                        reset = True
                    if "STOP" in received_message:
                        stop = True
            self._listOfPlayerId = self._listOfPlayerId.reverse()  # reverse list of ID to change the first player
        print("server stopped")




if __name__ == '__main__':
    server = Server(12800)
    server.start()