import socket
import traceback

class Communicator:
    def __init__(self, name, port):
        self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._name = name
        self._error = None
        self._port = port
        self._stop = False
        self._matrixSize = None
        self._dimension = None

    def connect(self):
        pass

    def send_message(self, message, connection):
        try:
            if self._error is not None:
                print(self._name+" should SEND: "+message+" but will send : "+self._error)
                connection.send(("ERROR/"+self._error).encode())
            else:
                print(self._name+" SEND: "+message)
                connection.send(message.encode())
        except (ConnectionAbortedError, ConnectionResetError) as e:
            self._error = "connection error"
        else:
            pass

    def send_played_cell(self, playedCell, connection):
        if len(playedCell)==2:
            command = ("CELL/"+str(playedCell[0])+"/"+str(playedCell[1]))

        elif len(playedCell)==3:
            command = ("CELL/" + str(playedCell[0]) + "/" + str(playedCell[1])+ "/" + str(playedCell[2]))
        self.send_message(command, connection)

    def read_message(self, connection):
        message = "ERROR"
        try:
            message = connection.recv(1024).decode()
        except (ConnectionAbortedError, ConnectionResetError) as e:
            self._error = "connection error"
            message = "ERROR"

        if message == "":
            message = "ERROR/received empty (server disconnected)"

        # If the server sends an error
        if "ERROR" in message:
            self._error = "ERROR : Problem with the other connection : "+str(message.split("/")[-1])
        return message

    def read_played_cell(self, received_message):
        #CELL/2/2
        print("RECEIVED MESSAGE FOR "+str(self._name)+" : "+str(received_message))
        split = received_message.split("/")
        if len(split) == self._dimension +1:
            if self._dimension == 2:
                cell = [int(split[1]), int(split[2])]
            if self._dimension == 3:
                cell = [int(split[1]), int(split[2]), int(split[3])]
        else:
            cell = received_message
        return cell

    def is_in(self, listOfMessages, message):
        for element in listOfMessages:
            if element in message:
                return True
        return False