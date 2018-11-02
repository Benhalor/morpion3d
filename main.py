#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pygame

import gui


class Data:
    """Used to pass data between different instances"""
    def __init__(self):
        self.__gameSize = 3
        self.__port = 12800
        self.__ip = '127.0.0.1'
        self.__server = None
        self.__client = None
        self.__starting = 0
        
    def __get_size(self):
        return self.__gameSize
    def __set_size(self, s):
        self.__gameSize = max(3, min(9, s))
    gameSize = property(__get_size, __set_size)
    
    def __get_port(self):
        return self.__port
    port = property(__get_port)
    
    def __get_ip(self):
        return self.__ip
    def __set_ip(self, ip):
        self.__ip = ip
    ip = property(__get_ip, __set_ip)
    
    def __get_server(self):
        return self.__server
    def __set_server(self, s):
        self.__server = s
    server = property(__get_server, __set_server)
    
    def __get_client(self):
        return self.__client
    def __set_client(self, c):
        self.__client = c
    client = property(__get_client, __set_client)
    
    def __get_starting(self):
        return self.__starting
    def __set_starting(self, s):
        self.__starting = s
    starting = property(__get_starting, __set_starting)




print("MAIN: start")

boolContinue = True

data = Data()
window = gui.Window(data)

while boolContinue:
    
    startingTime = pygame.time.get_ticks()
    
    window.draw()
    
    boolTime = True
    while boolTime and window.alive:
        if pygame.event.peek():
            e = pygame.event.poll()
            window.handle_event(e)
        
        
        boolTime = pygame.time.get_ticks() - startingTime < 33
    
    boolContinue = boolContinue and window.alive

if data.server is not None:
    data.server.stop()
    data.server.join()


print("MAIN: end")






















