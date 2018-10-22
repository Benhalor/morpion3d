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
    def __init__(self, port, dimension, matrixSize):
        Thread.__init__(self)
        self._numberOfPlayers = 2
        self._port = port
        self._listOfConnections = []
        self._listOfInfoConnections = []
        self._listOfPlayerId = []
        self._idCounter = 1 #begins to 1 because 0 id means the cell is not yet played
        self._matrixSize = matrixSize #assume it is a square matrix
        self._dimension = dimension
        self._matrix = np.zeros([self._matrixSize for i in range(self._dimension)])
        self._stop = False
        self._error = None
        print("Server started")


    def send_played_cell(self, played_cell):
        if len(played_cell)==2:
            self.connection.send(("CELL/"+str(played_cell[0])+"/"+str(played_cell[1])).encode())
        elif len(played_cell)==3:
            self.connection.send(("CELL/" + str(played_cell[0]) + "/" + str(played_cell[1])+ "/" + str(played_cell[2])).encode())


    def connect_clients (self):
        print("waiting for clients to connect")
        self._main_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._main_connection.bind(('', self._port))
        self._main_connection.listen(5)
        self._main_connection.settimeout(1)

        for i in range(self._numberOfPlayers):
            #id/_dimension/size #assume it is a square matrix
            success = False
            while not success and not self._stop:
                try:
                    tempConnection , tempsInfoConnection = self._main_connection.accept()
                except socket.timeout:
                    pass
                else:
                    success = True
            command = str(self._idCounter)+"/"
            command += str(self._dimension)+ "/"
            command += str(self._matrixSize)

            self.send_message(command, tempConnection)
            print((bytearray(self._idCounter)))
            self._listOfPlayerId.append(self._idCounter)
            self._listOfConnections.append(tempConnection)
            self._listOfInfoConnections.append(tempsInfoConnection)
            self._idCounter += 1
            print(tempsInfoConnection)
        print("Clients connected")

    def send_played_cell(self, played_cell, connection):
        if not self._stop:
            if len(played_cell) == 2:
                command = ("CELL/"+str(played_cell[0])+"/"+str(played_cell[1])).encode()
            elif len(played_cell) == 3:
                command = ("CELL/" + str(played_cell[0]) + "/" + str(played_cell[1])+ "/" + str(played_cell[2])).encode()
            try:
                connection.send(command)
                print("SERVER SEND PLAYED CELL" + command.decode())
            except (ConnectionAbortedError, ConnectionResetError):
                self._error = "OTHER_DISCONNECTED"
            else:
                pass

    def send_message(self, message, connection):
        if not self._stop:
            try:
                print("SERVER SEND: "+message)
                connection.send(message.encode())
            except (ConnectionAbortedError, ConnectionResetError):
                self._error = "OTHER_DISCONNECTED"
            else:
                pass

    def answer(self, connection, message):
        if not self._stop:
            try:
                if self._error is None:
                    print("SERVER ANSWER: " + message)
                    connection.send(message.encode())
                else:
                    connection.send(self._error.encode())
            except (ConnectionAbortedError, ConnectionResetError):
                self._error = "OTHER_DISCONNECTED"
            else:
                pass


    def read_message(self, connection):
        cell = "RESET"
        if not self._stop:
            try:
                cell = connection.recv(1024).decode()
            except (ConnectionAbortedError, ConnectionResetError):
                self._error = "OTHER_DISCONNECTED"
            else:
                pass

        return cell

    def run(self):
        self.connect_clients()
        stop = False

        while not stop:
            reset = False
            received_message = "WAIT"
            # Send the start signal to clients : START/0 for first player and START/1 for second player
            count = 0
            skipFirstCellSending = True  # This is because the first player dont need to read a cell
            for element in self._listOfPlayerId:
                i = element - 1  # -1 because ids begin to 1
                command = "START/" + str(count)
                self.send_message(command, self._listOfConnections[i])
                count += 1
            while not reset and not stop:

                for element in self._listOfPlayerId:
                    i = element - 1  # -1 because ids begin to 1
                    if not skipFirstCellSending:
                        self.send_played_cell(played_cell, self._listOfConnections[i])
                    else:
                        skipFirstCellSending = False
                    received_message = self.read_message(self._listOfConnections[i])

                    if "CELL" in received_message:
                        if self._dimension == 2:
                            split = received_message.split("/")
                            played_cell = [int(split[1]), int(split[2])]
                            self._matrix[played_cell[0], played_cell[1]] = self._listOfPlayerId[i]
                        if self._dimension == 3:
                            split = received_message.split("/")
                            played_cell = [int(split[1]), int(split[2]), int(split[3])]
                            self._matrix[played_cell[0], played_cell[1], played_cell[2]] = self._listOfPlayerId[i]
                        print("SERVER RECEIVED CELL FROM PLAYER "+str(self._listOfPlayerId[i]))
                        print(played_cell)
                        self.answer(self._listOfConnections[i], "OK")

                    if "RESET" in received_message:
                        
                        # Wait for the other to reset
                        received_message = self.read_message(self._listOfConnections[1-i])
                        if "RESET" in received_message:
                            reset = True
                            self.send_message("OK", self._listOfConnections[i])
                            self.send_message("OK", self._listOfConnections[1-i])
                        elif "STOP" in received_message:
                            stop = True
                            self.send_message("STOP", self._listOfConnections[i])

                    if self._error is not None:
                        for element_reset in self._listOfPlayerId:  # Send error message to the other player
                            j = element_reset - 1
                            if j != i:
                                self.send_message(self._error, self._listOfConnections[j])
                        self._error = None

                    if "STOP" in received_message:
                        stop = True

            self._listOfPlayerId.reverse()  # reverse list of ID to change the first player
            print("SERVER HAS BEEN RESET")

        self._main_connection.close()
        print("server stopped")

    def stop(self):
        self._stop = True

    def __repr__(self):
        return ("Server is on port : "+str(self._port)+" with dimension : " + str(self._dimension)+" with size : " +
              str(self._matrixSize))



if __name__ == '__main__':
    server = Server(12800, 3, 3)
    server.start()