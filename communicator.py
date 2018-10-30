import socket
import traceback


class Communicator:
    def __init__(self, name, port):
        self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._name = name
        self._error = None
        self._port = port
        self._stopBool = False
        self._matrixSize = None
        self._dimension = None

    def connect(self):
        pass

    def _send_message(self, message, connection):
        try:
            if self._error is not None:
                print(self._name + " should send : " + message + " but will send : " + self._error)
                connection.send(self._error.encode())
            else:
                print(self._name + " SEND: " + message)
                connection.send(message.encode())
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError) as e:
            self._error = "ERROR"
        else:
            pass

    def _send_played_cell(self, playedCell, connection):
        if len(playedCell) == 2:
            command = ("CELL/" + str(playedCell[0]) + "/" + str(playedCell[1]))

        elif len(playedCell) == 3:
            command = ("CELL/" + str(playedCell[0]) + "/" + str(playedCell[1]) + "/" + str(playedCell[2]))
        self._send_message(command, connection)

    def _read_message(self, connection):
        message = "ERROR"
        try:
            message = connection.recv(1024).decode()
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError) as e:
            self._error = "ERROR"
            message = "ERROR"

        # If connection is lost, sometimes no Exception is raised, but empty answer from the server
        if message == "":
            message = "ERROR"

        # If the server sends an error
        if "ERROR" in message:
            self._error = "ERROR"
        return message

    def _read_played_cell(self, received_message):
        """
        :input format: CELL/2/1 for 2D and CELL/1/0/2 for 3D:
        :output format: [2,1] for 2D and [1,0,2] for 3D
        """
        print(str(self._name) + "RECEIVED: " + str(received_message))
        split = received_message.split("/")
        if len(split) == self._dimension + 1:
            if self._dimension == 2:
                cell = [int(split[1]), int(split[2])]
            if self._dimension == 3:
                cell = [int(split[1]), int(split[2]), int(split[3])]
        else:
            cell = received_message
        return cell

    @staticmethod
    def _is_in(listOfMessages, message):
        """Check if one of the string of listOfMessage is in message"""
        for element in listOfMessages:
            if element in message:
                return True
        return False
