import socket


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
            print(self._name+" SEND: "+message)
            connection.send(message.encode())
        except (ConnectionAbortedError, ConnectionResetError) as e:
            self._error = str(e)
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
            self._error = str(e)
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