#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pygame
from time import sleep

import gui
import communicator


class Data:
    """Used to pass data between different instances"""
    def __init__(self):
        self.__gameSize = 3
        self.__port = 12800
        self.__ip = '127.0.0.1'
        self.__communicator = None
        self.__window = None
        self.__starting = 0
        self.__turn = 0
        self.__cell = (-1, -1, -1)
        
    def __get_size(self):
        return self.__gameSize
    def __set_size(self, s):
        if type(s) != int:
            raise TypeError("Argument 's': expected 'int', got " + str(type(s)))
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
        return self.__ip
    def __set_ip(self, ip):
        if type(ip) != str:
            raise TypeError("Argument 'ip': expected 'str', got " + str(type(ip)))
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
        return self.__starting
    def __set_starting(self, s):
        if type(s) != int:
            raise TypeError("Argument 's': expected 'int', got " + str(type(s)))
        if s not in (0,1,2):
            raise TypeError("Argument 's': expected 0, 1, or 2, got " + str(s))
        self.__starting = s
    starting = property(__get_starting, __set_starting)
    
    def __get_turn(self):
        return self.__turn
    def __set_turn(self, t):
        if type(t) != int:
            raise TypeError("Argument 't': expected 'int', got " + str(type(t)))
        if t not in (0,1,2):
            raise TypeError("Argument 't': expected 0, 1, or 2, got " + str(t))
        self.__turn = t
    turn = property(__get_turn, __set_turn)

    def __get_cell(self):
        return self.__cell
    def __set_cell(self, c):
        self.__cell = c
    cell = property(__get_cell, __set_cell)




print("MAIN: start")

boolContinue = True

data = Data()
data.window = gui.Window(data)

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
    

if data.communicator is not None:
    data.communicator.stop()
    data.communicator.join()


print("MAIN: end")






















