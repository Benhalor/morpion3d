#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#python PycharmProjects/morpion3d/server.py
from communicator import Communicator
from threading import Thread
import socket


class Server(Communicator, Thread):
    """Server
            An object acting as the server in the communication between two players
    """
    def __init__(self, data, name = "local server"):
        Thread.__init__(self)
        Communicator.__init__(self, name, data.port)
        
        self.__data = data
        self._matrixSize = data.gameSize # assuming it is a square matrix

        self._connection.bind(('', self._port))
        self._connection.listen(5)
        self._connection.settimeout(1)
        self.__stopBool = False
        
        self.__clientConnection = None

        print("SERVER: init")

    def __str__(self):
        return ("Server is on port : "+str(self._port)+" with size : " +
              str(self._matrixSize))
    
    def stop(self):
        """Stop the loop in the run method"""
        print("SERVER: stopping...")
        self.__stopBool = True
        
    def run(self):
        """Run method used for threading"""
        print("SERVER: started")
        
        self.__connect_client()

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
            print("SERVER: reset")

        self._connection.close()
        print("SERVER: end")


    def __connect_client(self):
        """Wait the two clients to connect. And send them the size of the matrix"""
        print("SERVER: waiting for client to connect")
        self._connection.settimeout(10)
        success = False
        while not success and not self.__stopBool:
            try:
                tempConnection , tempsInfoConnection = self._connection.accept()
                print("SERVER: received ", tempsInfoConnection)
            except socket.timeout:
                pass
            except Exception as e:
                print("SERVER: exception ", e)
            else:
                success = True
        
        if self.__stopBool:
            print("SERVER: aborting the search")
            return 0
        
        # Information sent to client : size
        command = str(self._matrixSize)
        self._send_message(command, tempConnection)
        self.__wait_message(tempConnection, ["OK", "ERROR"])  # Wait for confirmation
        
        self.__clientConnection = tempConnection

        self._connection.settimeout(1)
        print("SERVER: all clients connected")


    def __send_start_command_to_client(self):
        """ Send the start signal to clients : START/0 for first player and START/1 for second player"""
        command = "START/" + str(1 - self.__data.starting)
        self._send_message(command, self.__clientConnection)

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

    def __wait_message(self, connection, messages_to_wait):
        """ Wait one of the string in messages_to_wait and check that the gui is not stopped"""
        self._connection.settimeout(1.0)
        received_message = "WAIT"

        while not Communicator._is_in(messages_to_wait, received_message):
            try:
                received_message = self._read_message(connection)
            except Exception:
                pass

        return received_message