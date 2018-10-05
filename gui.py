
#Import library
import pygame
import time

from pygame.locals import *

class GameWindow :

	def __init__(self):
		pygame.init() #Initialization of the library

		self.screen = pygame.display.set_mode((640, 480)) #Creation of the window object

		start = time.time()

		fond = pygame.image.load("graphics/backgroundTest.jpg").convert()
		self.screen.blit(fond, (0, 0))
		self.screen.fill([10, 10, 70])

		#pygame.draw.ellipse(screen, RED, [225, 10, 50, 20], 2)

		pygame.display.flip()


		end = time.time()
		# Boucle infinie
		while end-start < 2:
			end = time.time()

window1 = GameWindow()


