#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 10:09:31 2018

@author: gabriel
"""

#python PycharmProjects/morpion3d/server.py
from communicator import Communicator
from threading import Thread
import numpy as np
import socket


class Server(Communicator, Thread):
    def __init__(self, port, dimension, matrixSize, name):
        Thread.__init__(self)
        Communicator.__init__(self, name, port)

        self._numberOfPlayers = 2
        self._listOfConnections = []
        self._listOfPlayerId = []
        self._idCounter = 1 #begins to 1 because 0 id means the cell is not yet played

        self._matrixSize = matrixSize #assume it is a square matrix
        self._dimension = dimension

        print("SERVER : STARTED")

    def __repr__(self):
        return ("Server is on port : "+str(self._port)+" with dimension : " + str(self._dimension)+" with size : " +
              str(self._matrixSize))

    def run(self):
        self.connect_clients()
        stop = False

        while not stop:

            reset = False
            skipFirstCellSending = True  # This is because the first player dont need to read a cell
            self.send_start_command_to_clients()
            played_cell = None

            while not reset and not stop:
                played_cell, reset, stop, skipFirstCellSending = self.play_a_turn(skipFirstCellSending, played_cell)

            # reverse list of ID to change the first player
            self._listOfPlayerId.reverse()
            print("SERVER HAS BEEN RESET")

        self._connection.close()
        print("SERVER STOPPED")

    def connect_clients (self):
        print("SERVER : WAITING FOR CLIENTS TO CONNECT")
        self._connection.bind(('', self._port))
        self._connection.listen(5)
        self._connection.settimeout(1)

        # Connect clients one by one (self._numberOfPlayers = 2 clients expected)
        for i in range(self._numberOfPlayers):
            success = False
            while not success and not self._stop:
                try:
                    tempConnection , tempsInfoConnection = self._connection.accept()
                    print(tempsInfoConnection)
                except socket.timeout:
                    pass
                except Exception as e:
                    print(e)
                else:
                    success = True

            # Information sent to client : id/_dimension/size
            command = str(self._idCounter)+"/"
            command += str(self._dimension)+ "/"
            command += str(self._matrixSize)
            self.send_message(command, tempConnection)

            # Append client to lists
            self._listOfPlayerId.append(self._idCounter)
            self._listOfConnections.append(tempConnection)

            self._idCounter += 1
        print("SERVER : ALL CLIENTS CONNECTED")

    def send_start_command_to_clients(self):
        # Send the start signal to clients : START/0 for first player and START/1 for second player
        count = 0
        for element in self._listOfPlayerId:
            i = element - 1  # -1 because ids begin to 1
            command = "START/" + str(count)
            self.send_message(command, self._listOfConnections[i])
            count += 1

    def play_a_turn(self, skipFirstCellSending, played_cell):
        reset = False
        stop = False

        for element in self._listOfPlayerId:
            i = element - 1  # -1 because ids begin to 1
            if not skipFirstCellSending:
                self.send_played_cell(played_cell, self._listOfConnections[i])
            else:
                skipFirstCellSending = False
            received_message = self.read_message(self._listOfConnections[i])

            #Player sends a played CELL
            if "CELL" in received_message:
                if self._dimension == 2:
                    split = received_message.split("/")
                    played_cell = [int(split[1]), int(split[2])]
                if self._dimension == 3:
                    split = received_message.split("/")
                    played_cell = [int(split[1]), int(split[2]), int(split[3])]
                print("SERVER RECEIVED CELL FROM PLAYER " + str(self._listOfPlayerId[i]))
                print(played_cell)
                self.send_message("OK", self._listOfConnections[i])

            # Player wants to reset game
            if "RESET" in received_message:
                # Wait for the other to reset
                received_message = self.read_message(self._listOfConnections[1 - i])
                if "RESET" in received_message:
                    reset = True
                    self.send_message("OK", self._listOfConnections[i])
                    self.send_message("OK", self._listOfConnections[1 - i])
                elif "STOP" in received_message:
                    stop = True
                    self.send_message("STOP", self._listOfConnections[i])

            # Player wants to stop
            if "STOP" in received_message:
                stop = True

        return played_cell, reset, stop, skipFirstCellSending

    def stop(self):
        self._stop = True

if __name__ == '__main__':
    server = Server(12800, 3, 3, "SERVER")
    server.start()