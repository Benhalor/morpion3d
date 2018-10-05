#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 10:09:31 2018

@author: gabriel
"""

import socket
import numpy as np

class Client():
    def __init__(self, name):
        self.name = name
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.matrixSize = (3,3,3)

    def connect(self):
        self.connection.connect(('localhost', 12800))
        print("Client " + self.name + " is joining server...")
        self.connection.send(b"JOIN")
        received_message = "DENIED"
        while(received_message != "ACCEPTED"):
            try:
                received_message = self.connection.recv(1024).decode()
            except Exception as e:
                print(e)
        print("Client " + self.name + " is connected to server.")

    def send_matrix(self, matrix):
        matrix = np.array(matrix)
        shape = matrix.shape
        if shape == self.matrixSize:
            command = "MATRIX/"+str(self.matrixSize[0])+"/"+str(self.matrixSize[1])+"/"+str(self.matrixSize[2])+"/"
            print(command.encode()+b"0")
        else:
            raise Exception("Matrix size is wrong")

    def close_client(self):
        self.connexion_avec_serveur.send(b"QUIT")

    def run(self):

        msg_recu = self.connection.recv(1024)
        if msg_recu == b"HLO":
            self.connection.send(b"HLO")
        else:
            raise Exception("Messge recu non valide : " + msg_recu.decode())
        command = input("Entrez une commande: ").replace("\n", "").split(" ")
        while "QUT" not in command:
            if len(command)==3:
                operateur = command[0].encode()
                nb1 = float(command[1])
                nb2 = float(command[2])
                nb1_byte = bytearray(struct.pack("d", nb1))
                nb2_byte = bytearray(struct.pack("d", nb2))
                self.connexion_avec_serveur.send(operateur + nb1_byte + nb2_byte)
                msg_recu = self.connexion_avec_serveur.recv(1024).decode()
                print("Valeur renvoyée: "+msg_recu)
            else:
                print("Mauvaise syntaxe. Exemple : ADD 1.23 55.3")
            command = input("Entrez une commande: ").replace("\n", "").split(" ")
        self.connexion_avec_serveur.send(b"QUT")

        print("Client fermé")

if __name__ == '__main__':
    client = Client("Gabriel")
    client.send_matrix([[[0,0,0],[0,0,0],[0,0,0]], [[0,0,0],[0,0,0],[0,0,0]], [[0,0,0],[0,0,0],[0,0,0]]])