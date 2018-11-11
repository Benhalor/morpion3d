import socket
from threading import Thread, Lock
from time import sleep

import gamesession


class Communicator(Thread):
    """Communicator
            An object with safe communication socket. Is the parent of Client and Server

            Usage example:
            Communicator is never used. Only children classes
        """

    def __init__(self, name, data):
        Thread.__init__(self)
        self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connection2 = None
        self.__name = name
        self._data = data
        self._error = None
        self._stopBool = False
        self.__running = False
        self._connected = False
        self.__PAanswer = -1  # Play Again answer
        self._connectionLock = Lock()

    def stop(self):
        """ Stop the Thread and the send STOP message to the other"""
        if self.__running:
            print(self.__name + ": stopping...")
        if self._connected:
            self._send_message("STOP", self._connection2)
        self._stopBool = True

    def run(self):
        print(self.__name + ": start")
        self.__running = True

        # Connect the two players
        self._start()

        while not self._stopBool:  # one loop iteration for each game session
            self.__PAanswer = -1
            reset = False
            self._init_game()

            if not self._stopBool:
                session = gamesession.GameSession(self._data)
            self._data.turn = self._data.starting

            while not reset and not self._stopBool:  # one loop iteration for each turn

                # My turn
                if self._data.turn == 1:
                    print(self.__name + ": waiting for the player to choose a cell")
                    while self._data.cell == (-1, -1, -1) and not self._stopBool:
                        sleep(0.001)  # Sleep 1 ms to release the processor

                    cell = self._data.cell
                    self._data.cell = (-1, -1, -1)

                    if not self._stopBool:
                        session.play_a_turn(1, cell)

                        if session.state in (3, 4, 5):  # if it is a valid play, send cell data to the other
                            self._send_played_cell(cell, self._connection2)
                            try:
                                # The other should reply "OK" to confirm
                                received_message = self._wait_message(["OK", "STOP", "ERROR"], self._connection2)
                                if self._error is None and "OK" in received_message:
                                    pass  # all is good
                                else:
                                    raise ConnectionError
                            except:
                                self._stopBool = True
                                self._data.window.raise_flag("disconnect")
                        if session.state == 3:  # valid play, game continues
                            self._data.turn = 2
                        elif session.state == 4:  # valid play, I won
                            reset = True
                        elif session.state == 5:  # valid play, draw
                            reset = True

                # the opponent's turn
                elif self._data.turn == 2:
                    print(self.__name + ": waiting for the other to play")
                    try:
                        # Receive a cell from the other. Example : CELL/1/1/2
                        received_message = self._wait_message(["CELL", "STOP", "ERROR"], self._connection2)
                        if self._error is None and "CELL" in received_message:
                            # Convert the message to a list of coordinates. Example : (0,1,2)
                            playedCell = Communicator._read_played_cell(received_message)
                            session.play_a_turn(2, playedCell)
                            # Confirm the reception
                            self._send_message("OK", self._connection2)
                            if session.state == 3:  # valid play, game continues
                                self._data.turn = 1
                            elif session.state == 4:  # valid play, the other won
                                reset = True
                            elif session.state == 5:  # valid play, draw
                                reset = True
                        else:
                            raise ConnectionError
                    except:
                        self._stopBool = True
                        self._data.window.raise_flag("disconnect")

                # data.turn is not correct
                else:
                    self.stop()

            # At the end of the game, ask me for Playing Again (PA)
            # The user enters the answer via the GUI
            while self.__PAanswer == -1 and not self._stopBool:
                sleep(0.001)

            if not self._stopBool:
                if self.__PAanswer == 0:  # Yes, I want to play again
                    success = False
                    while not success and not self._stopBool:
                        self._send_message("PA", self._connection2)  # Say the other I want to play again
                        try:
                            received_message = self._read_message(self._connection2)  # Read his answer
                            if self._error is None:
                                if "PA" in received_message:
                                    success = True
                                    self._data.starting = 3 - self._data.starting
                                    self._data.turn = 0
                                elif "STOP" in received_message:
                                    self._data.window.raise_flag("stop_no_PA")
                                    self.stop()

                            else:
                                self._stopBool = True
                        except socket.timeout:  # Socket timed out. Try again
                            pass
                        except Exception as e:  # Something unexpected happened. Quit
                            print("SERVER: exception ", e)
                            self._stopBool = True
                            self._data.window.raise_flag("disconnect")

                else:  # No, I dont want to play again
                    self._data.window.raise_flag("stop")
                    self.stop()

        print(self.__name + ": end")
        self._end()
        self.__running = False

    def _start(self):
        """This method is called once at the start of the thread run() method
        To be redefined by children classes"""
        pass

    def _init_game(self):
        """This method is called once per game session in the thread run() method
        To be redefined by children classes"""
        pass

    def _end(self):
        """This method is called once at the end of the thread run() method
        To be redifined by children classes"""
        pass

    def _send_message(self, message, connection):
        """Method for sending a message that catches the exceptions"""
        message += "#"  # the "#" symbol is a end-byte symbol, to know that it is the end of the message
        with self._connectionLock:
            try:
                if not self._connected:
                    print(self._name + ": cannot send message without connection")
                elif self._error is not None:
                    print(self.__name + " should send : " + message + " but will send : " + self._error)
                    connection.send(self._error.encode())
                else:
                    print(self.__name + " SEND: " + message)
                    connection.send(message.encode())
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError) as e:
                self._error = "ERROR"

    def _send_played_cell(self, playedCell, connection):
        """ Convert a cell (1,1,2) to a message CELL/1/1/2 and send it"""
        command = ("CELL/" + str(playedCell[0]) + "/" + str(playedCell[1]) + "/" + str(playedCell[2]))
        self._send_message(command, connection)

    def _read_message(self, connection):
        """Read a message from connection and return it. Catch the errors if any"""
        message = "ERROR"
        with self._connectionLock:
            try:
                if not self._connected:
                    print(self._name + ": cannot receive message without connection")
                message = Communicator._recv_clever(connection)  # Use a better method than the default recv method
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError) as e:
                message = "ERROR"

        # If connection is lost, sometimes no Exception is raised, but empty answer from the server
        if message == "":
            message = "ERROR"

        # If the server sends an error
        if "ERROR" in message:
            self._error = "ERROR"

        print(self.__name + " RECEIVED: " + str(message))
        return message

    @staticmethod
    def _recv_clever(connection):
        """ Read the characters one by one and stop when you see a "#" symbol. It means the end of the message"""
        message = ""
        received_string = ""
        while received_string != "#":
            message += received_string
            received_string = connection.recv(1).decode('utf-8')
        return message

    @staticmethod
    def _read_played_cell(received_message):
        """
        input format: CELL/1/0/2 
        output format: (1,0,2)
        """
        split = received_message.split("/")
        if len(split) == 4:
            return int(split[1]), int(split[2]), int(split[3])
        else:
            raise ValueError("Wrong cell format")

    def _wait_message(self, messages_to_wait, connection):
        """ Wait one of the string in messages_to_wait"""
        self._connection.settimeout(1.0)
        received_message = "WAIT"

        while not Communicator._is_in(messages_to_wait, received_message) and not self._stopBool:
            try:
                received_message = self._read_message(connection)
            except Exception:
                pass
            sleep(0.001)

        if not self._stopBool:
            return received_message
        else:
            return "STOP"

    @staticmethod
    def _is_in(listOfMessages, message):
        """Check if one of the string of listOfMessage is in message"""
        for element in listOfMessages:
            if element in message:
                return True
        return False

    def __get_pa_answer(self):
        return self.__PAanswer

    def __set_pa_answer(self, a):
        self.__PAanswer = a

    PAanswer = property(__get_pa_answer, __set_pa_answer)

    def __is_running(self):
        return self.__running

    running = property(__is_running)


class Server(Communicator):
    """Server
            An object acting as the server in the communication between two players
            
    """

    def __init__(self, data):
        Communicator.__init__(self, "SERVER", data)
        self._connection.bind(('0.0.0.0', self._data.port))
        self._connection.listen(5)
        self._connection.settimeout(1)

    def _start(self):
        """Redefining the start method from base class Communicator
        Wait the client to connect. And send the size of the matrix"""
        print("SERVER: waiting for client to connect")
        self._connection.settimeout(10)
        success = False
        while not success and not self._stopBool:
            try:
                tempConnection, tempsInfoConnection = self._connection.accept()
                print("SERVER: received ", tempsInfoConnection)
            except socket.timeout:  # Socket timed out. Try again
                pass
            except Exception as e:  # Something unexpected happened. Quit
                print("SERVER: exception ", e)
                self._stopBool = True
            else:
                success = True

        if self._stopBool:
            print("SERVER: aborting the search")
            return 0
        
        self._connected = True

        # Information sent to client : size
        self._send_message(str(self._data.gameSize), tempConnection)

        # Waiting for a confirmation from the client
        try:
            received_message = self._wait_message(["OK", "ERROR", "STOP"], tempConnection)
            if self._error is None and "OK" in received_message:
                pass  # all is good
            else:
                raise ConnectionError
        except:
            self._stopBool = True
            self._data.window.raise_flag("disconnect")
            return 0

        self._connection2 = tempConnection

        self._connection2.settimeout(1)
        self._data.starting = 1
        self._data.window.raise_flag("start 3D")
        print("SERVER: client connected")

    def _init_game(self):
        """Redefining the init_game method from base class Communicator
        Send the start signal to client : START/1 for first player and START/2 for second player"""
        command = "START/" + str(3 - self._data.starting)  # 2 -> 1 and 1 -> 2
        self._send_message(command, self._connection2)

    def _end(self):
        """Redefining the init_game method from base class Communicator
        Close the sockets"""
        with self._connectionLock:
            if self._connection2 is not None:
                self._connection2.close()
            self._connection.close()
            self._connected = False


class Client(Communicator):
    """Client
        An object acting as the client in the communication between two players
        
    """

    def __init__(self, data):
        Communicator.__init__(self, "CLIENT", data)
        self._connection.settimeout(10.0)

    def _start(self):
        """Redefining the start method from base class Communicator
        Try to connect the client to the server
        Raise error if server is unreachable
        When connected get size from the server"""
        print("CLIENT: connecting to server...")
        success = False
        while not success and not self._stopBool:
            try:
                self._connection.connect((self._data.ip, self._data.port))
            except socket.timeout:  # Socket timed out. Try again
                pass
            except Exception as e:  # Something unexpected happened. Quit
                print("CLIENT: exception ", e)
                self._stopBool = True
                self._data.window.raise_flag("conn failed")
            else:
                success = True

        if self._stopBool:
            return 0
        
        self._connected = True

        # Repeat the reception until message is not empty (can be empty if network communication is bad)
        received_message = ""
        while received_message == "" and not self._stopBool:
            try:
                # Expected message from server : "size"
                received_message = self._connection.recv(1024).decode().replace("#", "")
                print("CLIENT: received " + str(received_message))
                self._data.gameSize = int(received_message)
                self._send_message("OK", self._connection)  # Send confirmation
            except socket.timeout:  # Socket timed out. Try again
                pass
            except Exception as e:  # Something unexpected happened. Quit
                print("CLIENT: exception ", e)
                self._stopBool = True
                self._data.window.raise_flag("conn failed")

        if not self._stopBool:
            print("CLIENT: connected to server")
            self._connection2 = self._connection
            self._data.window.raise_flag("start 3D")
            return True
        else:
            return 0

    def _init_game(self):
        """Redefining the init_game method from base class Communicator
        Wait for the start message from server at beginning"""
        print("CLIENT: waiting for the start message")

        # Expected message : START/1 if first player or START/2 if second player
        while not self._stopBool:
            try:
                received_message = self._wait_message(["START", "STOP", "ERROR"], self._connection2)
                if self._error is None and "START" in received_message:
                    first = int(received_message.split("/")[-1])
                    if first == 1:
                        self._data.starting = 1
                    elif first == 2:
                        self._data.starting = 2
                    else:
                        raise ValueError("Wrong start message format")
                    return 0
                else:
                    raise ConnectionError
            except:
                self._stopBool = True
                self._data.window.raise_flag("disconnect")

    def _end(self):
        """Redefining the init_game method from base class Communicator
        Close the socket"""
        with self._connectionLock:
            self._connection.close()
            self._connected = False
