#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket

from communicator import Communicator
from threading import Thread
import gamesession
from morpionExceptions import *



class Server(Communicator, Thread):
    """Server
            An object acting as the server in the communication between two players
            
    """
    def __init__(self, data, name = "LOCAL SERVER"):
        Thread.__init__(self)
        Communicator.__init__(self, name, data.port)
        
        self.__data = data

        self._connection.bind(('', self._port))
        self._connection.listen(5)
        self._connection.settimeout(1)
        self.__stopBool = False
        self.__running = False
        
        self.__clientConnection = None

        print("SERVER: init")

    def __str__(self):
        return ("Server is on port : "+str(self._port)+" with size : " +
              str(self.__data.gameSize))
    
    def stop(self):
        """Stop the loop in the run method"""
        if self.__running:
            print("SERVER: stopping...")
        self.__stopBool = True
        
    def run(self):
        """Run method used for threading"""
        print("SERVER: started")
        self.__running = True
        
        self.__connect_client()

        while not self.__stopBool:

            reset = False

            # Init game
            self.__send_start_command_to_client()
            session = gamesession.GameSession(self.__data)
            self.__data.turn = self.__data.starting

            # Play
            while not reset and not self.__stopBool:
                
                if self.__data.turn == 1: # Server plays
                    while self.__data.cell == (-1, -1, -1):
                        pass
                    session.play_a_turn(1, self.__data.cell)
                    
                    if session.state == 3: # valid play, game continues
                        self.__data.turn = 2
                        self._send_played_cell(self.__data.cell, self.__clientConnection)
                        self.__clientConnection.settimeout(5.0)
                        try:
                            received_message = self.__wait_message(self.__clientConnection, ["OK", "STOP", "ERROR"])
                            if self._error is None:
                                if "STOP" in received_message:
                                    self.__stopBool = True
                                elif "ERROR" in received_message:
                                    raise ServerError()
                                elif "OK" in received_message:
                                    pass # all is good
                                else:
                                    raise ServerError()
                            else:
                                raise ServerError()
                        except Exception as e:
                            print(e, "//", received_message)
                            self.__stopBool = True
                            self.__data.window.raise_flag("disconnect")
                    elif session.state == 4: # valid play, server won
                        pass
                    elif session.state == 5: # valid play, draw
                        pass
                    
                    self.__data.cell = (-1, -1, -1)
                    
                elif self.__data.turn == 2: # Client plays
                    print("SERVER: waiting for the client to play")
                    try:
                        received_message = self.__wait_message(self.__clientConnection, ["CELL", "STOP", "ERROR"])
                        if self._error is None:
                            
                            if "CELL" in received_message:
                                playedCell = self._read_played_cell(received_message)
                                self._send_message("OK", self.__clientConnection)
                                session.play_a_turn(2, playedCell)
                                if session.state == 3: # valid play, game continues
                                    self.__data.turn = 1
                                elif session.state == 4: # valid play, client won
                                    pass
                                elif session.state == 5: # valid play, draw
                                    pass
                            
                            elif "STOP" in received_message:
                                self.__stopBool = True
                                
                            elif "ERROR" in received_message:
                                raise ServerError()
                                
                        else:
                            raise ServerError()
                         
                    except Exception as e:
                        self.__stopBool = True
                        self.__data.window.raise_flag("disconnect")

            # Reverse list of ID to change the first player for the next game
            """self.__listOfPlayerId.reverse()
            print("SERVER: reset")"""

        self._connection.close()
        print("SERVER: end")
        self.__running = False


    def __connect_client(self):
        """Wait the client to connect. And send the size of the matrix"""
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
        self._send_message(str(self.__data.gameSize), tempConnection)
        self.__wait_message(tempConnection, ["OK", "ERROR"])  # Wait for confirmation

        self.__clientConnection = tempConnection

        self._connection.settimeout(1)
        self.__data.starting = 1
        print("SERVER: client connected")


    def __send_start_command_to_client(self):
        """ Send the start signal to clients : START/0 for first player and START/1 for second player"""
        command = "START/" + str(3 - self.__data.starting) # 2 -> 1 and 1 -> 2
        self._send_message(command, self.__clientConnection)

    def __wait_message(self, connection, messages_to_wait):
        """ Wait one of the string in messages_to_wait"""
        connection.settimeout(1.0)
        received_message = "WAIT"

        while not Communicator._is_in(messages_to_wait, received_message) and not self.__stopBool:
            try:
                received_message = self._read_message(connection)
            except Exception:
                pass

        if not self.__stopBool:
            return received_message
        else:
            return "STOP"