#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
import tkinter
from tkinter import messagebox
import socket

import server
import client
import guiGameWindow3D


class Window:
    
    def __init__(self, data):
        self.__data = data
        print("GUI: init")
        pygame.init()
        self.__alive = True
        self.__background = pygame.image.load('graphics/metal.jpg')
        self.__screen = pygame.display.set_mode((640, 480))
        pygame.display.set_caption('Mega Morpion 3D')
        self.__screenName = "menu"
        self.__3Dwindow = None
    
    
    def draw(self):
        self.__screen.blit(self.__background,(0,0))
        if self.__screenName == "menu":
            self.__draw_text("MEGA MORPION 3D", (110, 30), size = 64)
            self.__draw_text("Press C to create a game with size " + str(self.__data.gameSize), (110, 280))
            self.__draw_text("Press P/M or +/- to change the game size", (110, 320))
            self.__draw_text("Press J to join a game at address " + self.__data.ip, (110, 400))
            self.__draw_text("Press I to change the IP address", (110, 440))
        elif self.__screenName == "game":
            self.__3Dwindow.step()
            self.__3Dwindow.draw_polygons()
        pygame.display.flip()
        
        
    def handle_event(self, e):
        if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
            self.stop()
            return 0
        
        if self.__screenName == "menu":
            if e.type == KEYDOWN:
                if e.key == K_p or e.key == K_PLUS:
                    self.__data.gameSize += 1
                elif e.key == K_m or e.key == K_MINUS:
                    self.__data.gameSize -= 1
                elif e.key == K_i:
                    window = tkinter.Tk()
                    ipbox = IPbox(window)
                    ipbox.mainloop()
                    self.__data.ip = ipbox.ip
                    del window
                    del ipbox    
                    
                elif e.key == K_c: 
                    # Get and show user IP
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    try:
                        # doesn't even have to be reachable
                        s.connect(('10.255.255.255', 1))
                        IP = s.getsockname()[0]
                    except:
                        IP = '127.0.0.1'
                    finally:
                        s.close()
                        
                    # create server    
                    try:
                        s = server.Server(self.__data)
                    except OSError:
                        self.__show_error("OSError", "Unable to start server. Port is blocked by firewall or another server is already running")
                        return 0
                    self.__data.server = s
                    self.__data.server.start()
                    
                    # Show IP to help the other to connect
                    print("Your IP is: " + str(IP))
                    self.__show_info("IP", "Your IP is : " + str(IP))
                    
                    self.__screenName = "game"
                    self.__3Dwindow = guiGameWindow3D.GameWindow3D(self, self.__data)
                    
                elif e.key == K_j: # create client
                    try:
                        c = client.Client(self.__data)
                        validity = c.connect()
                    except:
                        validity = False
                    if not validity:
                        self.__show_error("Error", "Unable to connect to " + self.__data.ip)
                        return 0
                    self.__screenName = "game"
                    self.__3Dwindow = guiGameWindow3D.GameWindow3D(self, self.__data)
                return 0
            
        elif self.__screenName == "game":
            if e.type == KEYDOWN: # camera rotation
                    if e.key == K_LEFT:
                        self.__3Dwindow.omegaz = -0.07
                    elif e.key == K_RIGHT:
                        self.__3Dwindow.omegaz = 0.07
                    elif e.key == K_UP:
                        self.__3Dwindow.omegax = 0.07
                    elif e.key == K_DOWN:
                        self.__3Dwindow.omegax = -0.07
            if e.type == KEYUP: # camera rotation
                if e.key == K_LEFT:
                    self.__3Dwindow.omegaz = 0.0
                elif e.key == K_RIGHT:
                    self.__3Dwindow.omegaz = 0.0
                elif e.key == K_UP:
                    self.__3Dwindow.omegax = 0.0
                elif e.key == K_DOWN:
                    self.__3Dwindow.omegax = 0.0
            if e.type == MOUSEBUTTONDOWN:
                """if e.button == 1:  # If left click, select cell if it is your turn
                    self.__cell = self.__gui.selectedCell"""
                if e.button == 3:
                    x = pygame.mouse.get_pos()[0]
                    self.__3Dwindow.omegaz = 0.0007 * (240 - x)
            if e.type == MOUSEBUTTONUP:
                """if e.button == 1:
                    self.__3Dwindow.selectedCell = (-1, -1, -1)"""
                if e.button == 3:  # If right click
                    self.__3Dwindow.omegaz = 0.0
            if e.type == MOUSEMOTION:
                self.__3Dwindow.detect_cell_pos(e.pos)

                
            
    def stop(self):
        self.__alive = False
        pygame.display.quit()
        pygame.quit()
        print("GUI: end")
        
    
    def __draw_text(self, text, coordinates, size = 24, color = (255, 255, 255)):
        font = pygame.font.Font(None, size)
        text = font.render(text, 1, color)
        self.__screen.blit(text, coordinates)
        
    def __show_error(self, title, text):
        root = tkinter.Tk()
        root.withdraw()
        tkinter.messagebox.showerror(title, text)
        root.update()
        del root
        
    def __show_info(self, title, text):
        root = tkinter.Tk()
        root.withdraw()
        tkinter.messagebox.showinfo(title, text)
        root.update()
        del root
        
    def __get_alive(self):
        return self.__alive
    alive = property(__get_alive)
    
    def __get_screen_name(self):
        return self.__screenName
    def __set_screen_name(self, s):
        if type(s) != str:
            raise TypeError("Argument 's': expected 'str', got " + str(type(s)))
        if s not in ('menu', 'game'):
            raise ValueError("Screen name " + s + ": no such screen")
        self.__screenName = s
    
    def __get_screen(self):
        return self.__screen
    screen = property(__get_screen)



class IPbox(tkinter.Frame):
    
    def __init__(self, window, **kwargs):
        self.__ip = '127.0.0.1'
        self.__window = window
        tkinter.Frame.__init__(self, self.__window, width=768, height=576, **kwargs)
        self.pack(fill=tkinter.BOTH)
        self.__labelIP = tkinter.Label(self, text="IP: ")
        self.__labelIP.grid(row=0, column=0)
        self.__entryIP = tkinter.Entry(self)
        self.__entryIP.insert(0, "127.0.0.1")
        self.__entryIP.grid(row=0, column=1)
        self.__OKbutton = tkinter.Button(self, text="OK", command=self.__OK)
        self.__OKbutton.grid(row=0, column=2)
        
    def __OK(self):
        self.__ip = self.__entryIP.get()
        self.__window.destroy()
        
    def __get_ip(self):
        return self.__ip
    ip = property(__get_ip)




























