#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from communicator import Communicator
from threading import Thread
import socket


class Server(Communicator, Thread):
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

        print("SERVER : STARTED")

    def __repr__(self):
        return ("Server is on port : "+str(self._port)+" with dimension : " + str(self._dimension)+" with size : " +
              str(self._matrixSize))

    def run(self):
        self.connect_clients()
        stop = False

        while not stop:

            reset = False
            skipFirstCellSending = True  # This boolean because the first player doesnt need to read a cell from server
            playedCell = None

            # Init game
            self.send_start_command_to_clients()

            # Play
            while not reset and not stop:
                playedCell, reset, stop, skipFirstCellSending = self.play_a_turn(skipFirstCellSending, playedCell)

            # Reverse list of ID to change the first player for the next game
            self.__listOfPlayerId.reverse()
            print("SERVER HAS BEEN RESET")

        self._connection.close()
        print("SERVER STOPPED")

    def connect_clients (self):
        print("SERVER : WAITING FOR CLIENTS TO CONNECT")

        # Connect clients one by one (self._numberOfPlayers = 2 clients expected)
        for i in range(self.__numberOfPlayers):
            success = False
            while not success and not self._stopBool:
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

    def send_start_command_to_clients(self):
        """ Send the start signal to clients : START/0 for first player and START/1 for second player"""
        count = 0
        for element in self.__listOfPlayerId:
            i = element - 1  # -1 because ids begin to 1
            command = "START/" + str(count)
            self._send_message(command, self.__listOfConnections[i])
            count += 1

    def play_a_turn(self, skipFirstCellSending, playedCell):
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

    def stop(self):
        self._stopBool = True


if __name__ == '__main__':
    size = 3
    while size < 3 or size > 9:
        try:
            size = int(input("What size do you want (3<= Size <= 9? "))
        except ValueError:
            print("Must be a number")

    server = Server(12800, 3, size, "SERVER")
    server.start()