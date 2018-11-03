#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from threading import Thread

from communicator import Communicator
from morpionExceptions import *
import gamesession


class Client(Communicator, Thread):
    """Client
        An object acting as the client in the communication between two players
        
    """
    def __init__(self, data, name = "LOCAL CLIENT"):
        Thread.__init__(self)
        Communicator.__init__(self, name, data.port)
        
        self.__data = data
        self.__address = data.ip
        self._connection.settimeout(1.0)
        self.__connected = False
        self.__stopBool = False
        self.__running = False
        
        print("CLIENT: init")
        
        self.connect()

    def __str__(self):
        if self._connected:
            return "Client : " + str(self._name) + " is connected on address : " + str(
                self.__address) + " with port : " + \
                   str(self._port)
        else:
            return "Client : " + str(self._name) + " is not connected"
    
    def run(self):
        """Run method used for threading"""
        print("CLIENT: started")
        self.__running = True

        while not self.__stopBool:
            
            reset = False

            # Init game
            self.__wait_for_start()
            
            session = gamesession.GameSession(self.__data)
            self.__data.turn = self.__data.starting

            # Play
            while not reset and not self.__stopBool:
                if self.__data.turn == 1: # Client plays
                    while self.__data.cell == (-1, -1, -1):
                        pass
                    session.play_a_turn(1, self.__data.cell)
                    
                    if session.state == 1: # space is not free
                        pass
                    elif session.state == 3: # valid play, game continues
                        self.__data.turn = 2
                        self._send_played_cell(self.__data.cell, self._connection)
                        self._connection.settimeout(5.0)
                        try:
                            received_message = self.__wait_message(["OK", "STOP", "ERROR"])
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
                        except:
                            self.__stopBool = True
                            self.__data.window.raise_flag("disconnect")
                        
                    elif session.state == 4: # valid play, client won
                        pass
                    elif session.state == 5: # valid play, draw
                        pass
                    
                    self.__data.cell = (-1, -1, -1)
                    
                elif self.__data.turn == 2: # Server plays
                    print("CLIENT: waiting for the server to play")
                    try:
                        received_message = self.__wait_message(["CELL", "STOP", "ERROR"])
                        if self._error is None:
                            
                            if "CELL" in received_message:
                                playedCell = self._read_played_cell(received_message)
                                self._send_message("OK", self._connection)
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
                         
                    except:
                        self.__stopBool = True
                        self.__data.window.raise_flag("disconnect")
                    
                    
            # Reverse list of ID to change the first player for the next game
            """self.__listOfPlayerId.reverse()
            print("SERVER: reset")"""

        self._connection.close()
        print("CLIENT: end")
        self.__running = False

    def connect(self):
        """try to connect the client to the server. Raise error if server is unreachable
        when connected get size from the server"""
        self._connection.connect((self.__address, self._port))
        print("CLIENT: connecting to server...")

        # Repeat the reception until message is not empty (can be empty if network communication is bad)
        received_message = ""
        while received_message == "" and not self.__stopBool:
            try:
                # Expected message from server : "size"
                received_message = self._connection.recv(1024).decode()
                print("CLIENT: received " + str(received_message))
                self.__data.gameSize = int(received_message)
                self._send_message("OK", self._connection)  # Send confirmation
            except Exception as e:
                print("CLIENT: exeception ", e)
        if not self.__stopBool:
            print("CLIENT: connected to server")
            self.__connected = True
            return True
        else:
            return False

    def disconnect(self):
        """Close the socket connection"""
        if self.__connected:
            self._connection.close()

    def __wait_for_start(self):
        """ Wait for the start message from server at beginning"""
        print("CLIENT: waiting for the start message")

        # Expected message : START/1 if first player or START/2 if second player
        received_message = self.__wait_message(["START", "STOP", "ERROR"])
        if self.__stopBool:
            return 0
        first = int(received_message.split("/")[-1])
        if self._error is None:
            if first == 1:
                self.__data.starting = 1
            elif first == 2:
                self.__data.starting = 2
            else:
                raise ServerError()
        else:
            raise ServerError()

    def __wait_message(self, messages_to_wait):
        """ Wait one of the string in messages_to_wait"""
        self._connection.settimeout(1.0)
        received_message = "WAIT"

        while not Communicator._is_in(messages_to_wait, received_message) and not self.__stopBool:
            try:
                received_message = self._read_message(self._connection)
            except Exception:
                pass
        
        if not self.__stopBool:
            return received_message
        else:
            return "STOP"

    def stop(self):
        """Stop the loop in the run method"""
        if self.__running:
            print("CLIENT: stopping...")
        self.disconnect()
        self.__stopBool = True


