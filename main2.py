#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 09:50:34 2018

@author: armand
"""
#python PycharmProjects/morpion3d/main.py

import client
import guiMainWindow
import random
import gameengine
from threading import Thread
#TEST

me = gameengine.Player('Gabriel')
opponent = gameengine.Player('Opponent')
game = gameengine.Game(me, opponent, 3, True)
game.start()

client1 = client.Client("Sylvestre", 'localhost', 12800, [3,3])
client1.connect()


gui = guiMainWindow.MainWindow()

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
