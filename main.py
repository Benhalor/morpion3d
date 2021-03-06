#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
main.py
This file should be launched by the user to start the game
Usually, you have to write "python main.py" in a terminal (in the same location of course)

It contains the Data class and the GUI main routine
"""

import pygame
from time import sleep
from threading import Lock

import gui
import communicator


class Data:
    """Used to pass data between different instances
    A lock is used in the setters and getters to make sure they are thread-safe
    """
    def __init__(self):
        self.__gameSize = 3
        self.__port = 12800
        self.__ip = '127.0.0.1'
        self.__communicator = None
        self.__window = None
        self.__starting = 0
        self.__turn = 0
        self.__cell = (-1, -1, -1)
        self.__lowConfig = False
        self.__lock = Lock()
        
    def __get_size(self):
        with self.__lock:
            s = self.__gameSize
        return s
    def __set_size(self, s):
        if type(s) != int:
            raise TypeError("Argument 's': expected 'int', got " + str(type(s)))
        with self.__lock:
            self.__gameSize = max(3, min(9, s))
    gameSize = property(__get_size, __set_size)
    
    def __get_window(self):
        return self.__window
    def __set_window(self, w):
        if type(w) != gui.Window:
            raise TypeError("Argument 'w': expected 'Window', got " + str(type(w)))
        self.__window = w
    window = property(__get_window, __set_window)
    
    def __get_port(self):
        return self.__port
    port = property(__get_port)
    
    def __get_ip(self):
        with self.__lock:
            ip = self.__ip
        return ip
    def __set_ip(self, ip):
        if type(ip) != str:
            raise TypeError("Argument 'ip': expected 'str', got " + str(type(ip)))
        with self.__lock:
            self.__ip = ip
    ip = property(__get_ip, __set_ip)
    
    def __get_comm(self):
        return self.__communicator
    def __set_comm(self, c):
        if type(c) != communicator.Server and type(c) != communicator.Client:
            raise TypeError("Argument 'c': expected 'communicator', got " + str(type(c)))
        self.__communicator = c
    communicator = property(__get_comm, __set_comm)
    
    def __get_starting(self):
        with self.__lock:
            s = self.__starting
            return s
    def __set_starting(self, s):
        if type(s) != int:
            raise TypeError("Argument 's': expected 'int', got " + str(type(s)))
        if s not in (0,1,2):
            raise TypeError("Argument 's': expected 0, 1, or 2, got " + str(s))
        with self.__lock:
            self.__starting = s
    starting = property(__get_starting, __set_starting)
    
    def __get_turn(self):
        with self.__lock:
            t = self.__turn
        return t
    def __set_turn(self, t):
        if type(t) != int:
            raise TypeError("Argument 't': expected 'int', got " + str(type(t)))
        if t not in (0,1,2):
            raise TypeError("Argument 't': expected 0, 1, or 2, got " + str(t))
        with self.__lock:
            self.__turn = t
    turn = property(__get_turn, __set_turn)

    def __get_cell(self):
        with self.__lock:
            c = self.__cell
        return c
    def __set_cell(self, c):
        if type(c) != tuple:
            raise TypeError("Argument 'c': expected 'tuple', got " + str(type(c)))
        if len(c) != 3:
            raise ValueError("Argument c should have 3 elements, but has " + str(len(c)))
        with self.__lock:
            self.__cell = c
    cell = property(__get_cell, __set_cell)
    
    def __get_conf(self):
        with self.__lock:
            c = self.__lowConfig
        return c
    def __set_conf(self, c):
        if type(c) != bool:
            raise TypeError("Argument 'c': expected 'bool', got " + str(type(c)))
        with self.__lock:
            self.__lowConfig = c
    lowConfig = property(__get_conf, __set_conf)




print("MAIN: start")

boolContinue = True

data = Data()
data.window = gui.Window(data)

# GUI main routine
while boolContinue:
    
    startingTime = pygame.time.get_ticks()
    
    data.window.draw()
    
    boolTime = True
    while boolTime and data.window.alive:
        if pygame.event.peek():
            e = pygame.event.poll()
            data.window.handle_event(e)
        data.window.handle_flags()
        
        if pygame.time.get_ticks() - startingTime < 33:
            sleep(0.001)
        else:
            boolTime = False
    
    boolContinue = boolContinue and data.window.alive
    

if data.communicator is not None and data.communicator.running:
    data.communicator.stop()
    data.communicator.join()


print("MAIN: end")






















