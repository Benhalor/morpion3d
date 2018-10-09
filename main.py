#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 09:50:34 2018

@author: armand
"""
import client
import guiMainWindow
from threading import Thread
#TEST

client1 = client.Client("Gabriel", 'localhost', 12800)
client1.connect()

client2 = client.Client("Sylvestre", 'localhost', 12800)
client2.connect()

gui = guiMainWindow.MainWindow()

matrix = client1.wait_the_other_to_play()
print(matrix)
gui.send_state_matrix(matrix)

while(True):
    # The game engine returns the matrix A with the new play
    played_cell = gui.get_played_cell()
    client1.play(played_cell)
    matrix = client1.wait_the_other_to_play()
    gui.send_state_matrix(matrix)
