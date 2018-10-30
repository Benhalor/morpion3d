#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#python PycharmProjects/morpion3d/server.py
from communicator import Communicator
from threading import Thread
import tkinter
import socket


class Server(Communicator, Thread):
    """Server
            A client is used to get messages from clients and send them

    Usage example:
        server = Server(12800, 3, 3, "SERVER")
        server.start()
    """
    def __init__(self, port, dimension, matrixSize, name):
        Thread.__init__(self)
        Communicator.__init__(self, name, port)

        self.__numberOfPlayers = 2
        self.__listOfConnections = []
        self.__listOfPlayerId = []
        self.__idCounter = 1 #begins to 1 because 0 id means the cell is not yet played

        self._matrixSize = matrixSize #assume it is a square matrix
        self._dimension = dimension

        self._connection.bind(('', self._port))
        self._connection.listen(5)
        self._connection.settimeout(1)
        self.__stopBool = False

        print("SERVER : STARTED")

    def __str__(self):
        return ("Server is on port : "+str(self._port)+" with dimension : " + str(self._dimension)+" with size : " +
              str(self._matrixSize))
    
    def stop(self):
        """Stop the loop in the run method"""
        self.__stopBool = True
        
    def run(self):
        """Run method used for threading"""
        self.__connect_clients()

        while not self.__stopBool:

            reset = False
            skipFirstCellSending = True  # This boolean because the first player doesnt need to read a cell from server
            playedCell = None

            # Init game
            self.__send_start_command_to_clients()

            # Play
            while not reset and not self.__stopBool:
                playedCell, reset, self.__stopBool, skipFirstCellSending = self.__play_a_turn(skipFirstCellSending, playedCell)

            # Reverse list of ID to change the first player for the next game
            self.__listOfPlayerId.reverse()
            print("SERVER HAS BEEN RESET")

        self._connection.close()
        print("SERVER STOPPED")

    def __connect_clients(self):
        """Wait the two clients to connect. And send them the dimension and size of the matrix"""
        print("SERVER : WAITING FOR CLIENTS TO CONNECT")
        # Connect clients one by one (self._numberOfPlayers = 2 clients expected)
        for i in range(self.__numberOfPlayers):
            success = False
            while not success and not self.__stopBool:
                try:
                    tempConnection , tempsInfoConnection = self._connection.accept()
                    print(tempsInfoConnection)
                except socket.timeout:
                    pass
                except Exception as e:
                    print(e)
                else:
                    success = True

            # Information sent to client : id/dimension/size
            command = str(self.__idCounter)+"/"
            command += str(self._dimension)+ "/"
            command += str(self._matrixSize)
            self._send_message(command, tempConnection)

            # Append client to lists
            self.__listOfPlayerId.append(self.__idCounter)
            self.__listOfConnections.append(tempConnection)

            self.__idCounter += 1
        print("SERVER : ALL CLIENTS CONNECTED")

    def __send_start_command_to_clients(self):
        """ Send the start signal to clients : START/0 for first player and START/1 for second player"""
        count = 0
        for element in self.__listOfPlayerId:
            i = element - 1  # -1 because ids begin to 1
            command = "START/" + str(count)
            self._send_message(command, self.__listOfConnections[i])
            count += 1

    def __play_a_turn(self, skipFirstCellSending, playedCell):
        """Play a turn for each client : send him the last cell, and then get his played cell"""
        reset = False
        stop = False

        #  Clients play one by one
        for element in self.__listOfPlayerId:
            i = element - 1  # -1 because ids begin to 1

            # Send the cell played by the opponent. Is skipped for the first turn of first player.
            if not skipFirstCellSending and playedCell is not None:
                self._send_played_cell(playedCell, self.__listOfConnections[i])
            else:
                skipFirstCellSending = False

            # Read message from the player
            received_message = self._read_message(self.__listOfConnections[i])

            # Player sends a played CELL
            if "CELL" in received_message:
                playedCell = self._read_played_cell(received_message)  # Decode cell
                self._send_message("OK", self.__listOfConnections[i])  # Send confirmation

            # Player wants to reset game
            if "RESET" in received_message:

                # Wait for the other to reset
                received_message = ""
                while not Communicator._is_in(["ERROR", "RESET", "STOP"], received_message):
                    try:
                        received_message = self._read_message(self.__listOfConnections[1 - i])
                    except Exception:
                        pass

                # Other also wants to reset
                if "RESET" in received_message:
                    print("SERVER RESET")
                    reset = True
                    self._send_message("OK", self.__listOfConnections[i])
                    self._send_message("OK", self.__listOfConnections[1 - i])
                    break

                # Other wants to stop, or communication error
                elif "STOP" in received_message or "ERROR" in received_message:
                    print("SERVER RESET STOP")
                    stop = True
                    self._send_message("STOP", self.__listOfConnections[i])
                    break

            # ERROR : happens because of communication issue (client disconnected)
            if "ERROR" in received_message:
                print("SERVER COMMUNICATION ERROR")
                try:
                    self.__listOfConnections[1 - i].send(self._error.encode())
                except (ConnectionAbortedError, BrokenPipeError):
                    pass
                stop = True
                break

            # Player wants to stop
            if "STOP" in received_message:
                print("SERVER STOP")
                stop = True
                break

        return playedCell, reset, stop, skipFirstCellSending


if __name__ == '__main__':
    # Show IP of the server
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    print("Your IP is : " + IP)

    # Ask size
    size = 0
    while size < 3 or size > 9:
        try:
            size = int(input("What size do you want (3<= Size <= 9? "))
        except ValueError:
            print("Must be a number")

    server = Server(12800, 3, size, "SERVER")
    server.start()