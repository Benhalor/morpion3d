#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 09:50:34 2018

@author: armand
"""
#python PycharmProjects/morpion3d/main.py

import client
import guiMainWindow
import gameengine
from threading import Thread

name = "Sylvestre"

#Creat client, connect to serer, and get grid dimension and size.
client1 = client.Client(name, 'localhost', 12800)
client1.connect()
dimension = client1.dimension
print("Dimension for player " +name +": " +str(dimension))
matrixSize = client1.matrixSize
print("matrixSize for player " +name +": " +str(matrixSize))

#Start a game engine
me = gameengine.Player(name)
opponent = gameengine.Player('Opponent')
game = gameengine.Game(me, opponent, matrixSize, dimension == 2)
game.start(client1.playerId)

#start GUI
gui = guiMainWindow.MainWindow(matrixSize)
gui.start()


#LOOP
played_cell = client1.wait_the_other_to_play()
if -1 not in played_cell:
    print(played_cell)
    opponent.play(played_cell)#return victory, defeat, or invalid
    gui.set_message(game.message)
    print(game.message)
    matrix = game.grid.table
    gui.send_state_matrix(matrix)

while(True):
    played_cell = gui.get_played_cell()
    played_cell = client1.play(played_cell)
    me.play(played_cell)
    gui.set_message(game.message)
    print(game.message)
    matrix = game.grid.table
    gui.send_state_matrix(matrix)
    played_cell = client1.wait_the_other_to_play()
    opponent.play(played_cell)
    gui.set_message(game.message)
    print(game.message)
    matrix = game.grid.table
    gui.send_state_matrix(matrix)
