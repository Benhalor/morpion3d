#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
import tkinter
from tkinter import messagebox
import socket
from threading import Lock

import communicator
import guiGameWindow3D


class Window:
    """A pygame window
    Uses pygame events to get the user inputs
    Uses flags (see raise_flag and handle_flags methods) to interact with other threads
    
    Public attributes:
        alive (bool): if the window is alive or not
    
    """
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
        self.__flagLock = Lock()
    
    
    def draw(self):
        """Draws the screen"""
        self.__screen.blit(self.__background,(0,0))
        if self.__screenName == "menu":
            self.__draw_text("MEGA MORPION 3D", (110, 30), size = 64)
            self.__draw_text("Press C to create a game with size " + str(self.__data.gameSize), (110, 200))
            self.__draw_text("Press P/M or +/- to change the game size", (110, 240))
            self.__draw_text("Press J to join a game at address " + self.__data.ip, (110, 320))
            self.__draw_text("Press I to change the IP address", (110, 360))
            self.__draw_text("Press Z to view credits information", (110, 440))
            if self.__data.lowConfig:
                self.__draw_text("Currently using the high performances configuration", (110, 140))
                self.__draw_text("Press T for prettier graphics", (110, 155))
            else:
                self.__draw_text("Currently using the pretty graphics configuration", (110, 140))
                self.__draw_text("Press T for better performances", (110, 155))
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
        elif self.__screenName == "waiting":
            self.__draw_text("MEGA MORPION 3D", (110, 30), size = 64)
            self.__draw_text("waiting ...", (220, 208), size = 64)
        pygame.display.flip()
        
        
    def handle_event(self, e):
        """Does an action depending on the event and the current screen"""
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
                    ipbox = IPbox()
                    ipbox.mainloop()
                    self.__data.ip = ipbox.ip
                    del ipbox 
                elif e.key == K_z:
                    self.__show_info("Credits", "This software project was written as part of the Centralesupélec 2018 object oriented programming course.\n\nAuthors:\n\tArmand Bouvier\n\tGabriel Moneyron\n\tSylvestre Prabakaran")
                elif e.key == K_t:
                    self.__data.lowConfig = not(self.__data.lowConfig)
                    
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
                    
                    self.__screenName = "waiting"
                    
                elif e.key == K_j: # create client
                    try:
                        c = communicator.Client(self.__data)
                    except:
                        self.__show_error("Error", "Unable to connect to " + self.__data.ip)
                        return 0
                    self.__data.communicator = c
                    self.__data.communicator.start()
                    self.__screenName = "waiting"
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
        """Takes a flag at the top of the stack and does something depending on it
        Used to interact with other threads"""
        self.__flagLock.acquire()
        if self.__flags:
            flag = self.__flags.pop()
        else:
            self.__flagLock.release()
            return 0
        self.__flagLock.release()
        print("GUI: received flag: "+flag)
        if flag == "stop":
            self.__stop()
        elif flag == "start 3D":
            self.__screenName = "game"
            self.__3Dwindow = guiGameWindow3D.GameWindow3D(self.__data)
        elif flag == "victory":
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
            self.__stop()
        elif flag == "conn failed":
            self.__show_error('Network', 'Failed to connect')
            self.__stop()
        elif flag == "stop_no_PA":
            self.__show_error('Play Again', 'The other player doesn\'t want to play again')
            self.__stop()
        elif flag == "play again":
            root = tkinter.Tk()
            root.withdraw()
            answer = tkinter.messagebox.askyesno("Question", "Do you want to play again?")
            root.update()
            del root
            if answer:
                self.__data.communicator.PAanswer = 0
                self.__3Dwindow = guiGameWindow3D.GameWindow3D(self.__data)
            else:
                self.__data.communicator.PAanswer = 1
                self.__stop()
            
    def __stop(self):
        """Kills the pygame window"""
        self.__alive = False
        pygame.display.quit()
        pygame.quit()
        print("GUI: end")
        
    def send_grid(self, grid):
        """Sends the given grid to the 3D window""" 
        if self.__3Dwindow is not None:
            self.__3Dwindow.stateMatrix = grid
            
    def highlight_played_cell(self, cell):
        """Gives a pink color to the given cell
        Calls the corresponding method of the 3D window"""
        if type(cell) != tuple:
            raise TypeError("Argument 'cell': expected 'tuple', got " + str(type(cell)))
        if len(cell) != 3:
            raise ValueError("Tuple 'cell' should have 3 elements but has " + len(cell))
        self.__3Dwindow.highlight_played_cell(cell)
        
    def highlight_winning_cell(self, cell):
        """Gives a blue color to the given cell
        Calls the corresponding method of the 3D window"""
        if type(cell) != tuple:
            raise TypeError("Argument 'cell': expected 'tuple', got " + str(type(cell)))
        if len(cell) != 3:
            raise ValueError("Tuple 'cell' should have 3 elements but has " + len(cell))
        self.__3Dwindow.highlight_winning_cell(cell)
        
    def raise_flag(self, flag):
        """Put a flag on top of the stack
        Usually called by other thread"""
        if type(flag) != str:
            raise TypeError("Argument 'flag': expected 'str', got " + str(type(flag)))
        self.__flagLock.acquire()
        self.__flags.append(flag)
        self.__flagLock.release()
        
    
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
    
    def __get_screen(self):
        return self.__screen
    screen = property(__get_screen)



class IPbox(tkinter.Frame):
    """A simple dialog box that asks the user to enter an IP address"""
    def __init__(self):
        self.__ip = '127.0.0.1'
        self.__window = tkinter.Tk()
        self.__window.title("Enter an IP address")
        tkinter.Frame.__init__(self, self.__window)
        self.pack(fill=tkinter.BOTH)
        self.__labelIP = tkinter.Label(self, text="IP: ")
        self.__labelIP.grid(row=0, column=0)
        self.__entryIP = tkinter.Entry(self)
        self.__entryIP.insert(0, "127.0.0.1")
        self.__entryIP.grid(row=0, column=1)
        self.__OKbutton = tkinter.Button(self, text="OK", command=self.__OK)
        self.__OKbutton.grid(row=0, column=2)
        self.__window.bind('<Return>', self.__enter)
        
    def __OK(self):
        self.__ip = self.__entryIP.get()
        self.__window.destroy()
        
    def __enter(self, event):
        self.__OK()
        
    def __get_ip(self):
        return self.__ip
    ip = property(__get_ip)




