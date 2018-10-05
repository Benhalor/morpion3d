#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 10:09:31 2018

@author: gabriel
"""

#python PycharmProjects/morpion3d/server.py
import socket
from threading import Thread

class Server(Thread):
    def __init__(self, port):
        Thread.__init__(self)
        self.numberOfPlayers = 2
        self.port = port
        self.listOfConnections = []
        self.listOfInfoConnections = []
        self.idCounter = 0
        print("Server started")

    def connect_clients (self):
        print("waiting for clients to connect")
        self.main_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.main_connection.bind(('', self.port))
        self.main_connection.listen(5)


        for i in range(self.numberOfPlayers):
            tempConnection , tempsInfoConnection = self.main_connection.accept()
            tempConnection.send(str(self.idCounter).encode())
            print((bytearray(self.idCounter)))
            self.idCounter+=1
            self.listOfConnections.append(tempConnection)
            self.listOfInfoConnections.append(tempsInfoConnection)
            print(tempsInfoConnection)
        print("Clients connected")

    def run(self):
        received_message = "OK"
        while (True):
            for i in range (self.numberOfPlayers):
                self.listOfConnections[i].send(b"YOURTURN")
                received_message = self.listOfConnections[i].recv(1024).decode()
        print("run")


if __name__ == '__main__':
    server = Server(12800)
    server.connect_clients()