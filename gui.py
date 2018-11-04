#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
import tkinter
from tkinter import messagebox
import socket

import communicator
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
        self.__boolRightMB = False
        self.__flags = []
    
    
    def draw(self):
        self.__screen.blit(self.__background,(0,0))
        if self.__screenName == "menu":
            self.__draw_text("MEGA MORPION 3D", (110, 30), size = 64)
            self.__draw_text("Press C to create a game with size " + str(self.__data.gameSize), (110, 280))
            self.__draw_text("Press P/M or +/- to change the game size", (110, 320))
            self.__draw_text("Press J to join a game at address " + self.__data.ip, (110, 400))
            self.__draw_text("Press I to change the IP address", (110, 440))
        elif self.__screenName == "game":
            if self.__data.communicator.running:
                if self.__data.turn == 0:
                    self.__draw_text("Initiating the game...", (475,5))
                elif self.__data.turn == 1:
                    self.__draw_text("It is your turn!", (530,5))
                elif self.__data.turn == 2:
                    self.__draw_text("Waiting for the opponent to play...", (367,5))
            else:
                self.__draw_text("Game has ended", (505,5))
            self.__draw_text("Use the left mouse button to pick a cell", (5,432))
            self.__draw_text("Use the arrow keys or the right mouse button to rotate the view", (5, 448))
            self.__draw_text("Press ESC or close the window to quit", (5, 464))
            self.__3Dwindow.step()
            self.__3Dwindow.draw_polygons()
        pygame.display.flip()
        
        
    def handle_event(self, e):
        if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
            self.__stop()
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
                        s = communicator.Server(self.__data)
                    except OSError:
                        self.__show_error("Error", "Unable to start server. Port may be blocked by firewall or another server is already running. Please try again in a minute")
                        return 0
                    self.__data.communicator = s
                    self.__data.communicator.start()
                    
                    # Show IP to help the other to connect
                    print("Your IP is: " + str(IP))
                    self.__show_info("IP", "Your IP is : " + str(IP))
                    
                    self.__screenName = "game"
                    self.__3Dwindow = guiGameWindow3D.GameWindow3D(self, self.__data)
                    
                elif e.key == K_j: # create client
                    try:
                        c = communicator.Client(self.__data)
                    except:
                        self.__show_error("Error", "Unable to connect to " + self.__data.ip)
                        return 0
                    self.__data.communicator = c
                    self.__data.communicator.start()
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
                if e.button == 1:  # If left click, select cell if it is your turn
                    if self.__data.turn == 1:
                        self.__data.cell = self.__3Dwindow.selectedCell
                if e.button == 3:
                    self.__boolRightMB = True
            if e.type == MOUSEBUTTONUP:
                """if e.button == 1:
                    self.__data.cell = (-1, -1, -1)"""
                if e.button == 3:  # If right click
                    self.__boolRightMB = False
                    self.__3Dwindow.omegaz = 0.0
            if self.__boolRightMB:
                x = pygame.mouse.get_pos()[0]
                self.__3Dwindow.omegaz = 0.0005 * (320 - x)
            if e.type == MOUSEMOTION:
                self.__3Dwindow.detect_cell_pos(e.pos)

    def handle_flags(self):
        if self.__flags:
            flag = self.__flags.pop()
            if flag == "victory":
                self.draw()
                self.__show_info('Victory', 'You have won! Congratulations.')
                self.raise_flag("play again")
            elif flag == "defeat":
                self.draw()
                self.__show_info('Defeat', 'You have lost. Too bad.')
                self.raise_flag("play again")
            elif flag == "draw":
                self.draw()
                self.__show_info('Draw', "It's a draw!")
                self.raise_flag("play again")
            elif flag == "disconnect":
                self.__show_error('Network', 'Connection aborted')
            elif flag == "conn failed":
                self.__show_error('Network', 'Failed to connect')
            elif flag == "play again":
                root = tkinter.Tk()
                root.withdraw()
                answer = tkinter.messagebox.askyesno("Question", "Do you want to play again?")
                root.update()
                del root
                if answer:
                    self.__data.communicator.PAanswer = 0
                    self.__3Dwindow = guiGameWindow3D.GameWindow3D(self, self.__data)
                else:
                    self.__data.communicator.PAanswer = 1
            
    def __stop(self):
        self.__alive = False
        pygame.display.quit()
        pygame.quit()
        print("GUI: end")
        
    def send_grid(self, grid):
        if self.__3Dwindow is not None:
            self.__3Dwindow.stateMatrix = grid
            
    def highlight_played_cell(self, cell):
        self.__3Dwindow.highlight_played_cell(cell)
        
    def highlight_winning_cell(self, cell):
        self.__3Dwindow.highlight_winning_cell(cell)
        
    def raise_flag(self, flag):
        self.__flags.append(flag)
        
    
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
        self.__window.title("Enter an IP address")
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




