from Entity import *
from State import *
from Button import *
from Room import *
from Trees import *
from pygame import *
from pygame.locals import *
from sys import *
from math import *
from random import *
from time import *
from csv import *
from pickle import *

def timer(function, *args):
		start = time()
		function(*args)
		end = time()
		print function.__name__, ":", end - start 

def stop_until_click():
	run = True
	while run:
		for evnt in event.get():
			if evnt.type == MOUSEBUTTONDOWN:
				run = False
			if evnt.type == QUIT:
				import sys
				sys.exit()
 
class TD(State):

	def setup(self):
		self.gold = 0
		self.lives = 20
		self.time = 0

		self.towers = []
		self.entities = []

		self.tile_length = 32
		self.world_width = 29
		self.world_height = 26
		self.tiles = []

	#returns the x value of the mouse releative to the screen
	def mouse_x(self):
		return mouse.get_pos()[0]

	#returns the y value of the mouse releative to the screen
	def mouse_y(self):
		return mouse.get_pos()[1]

	def valid_square(self):
		x = self.mouse_x()/self.tile_length
		y = self.mouse_y()/self.tile_length
		if 1 < x < self.world_width - 2 and 1 < y < self.world_height - 2:
			if not (self.tiles[x][y].blocked or self.tiles[x + 1][y].blocked or self.tiles[x][y + 1].blocked or self.tiles[x + 1][y + 1]):
				return all([self.pathfind(path[0], path[1]) for path in self.paths])

	def click_began(self):
		for button in self.buttons:
			if button.rect.collidepoint(mouse.get_pos()):
				button.action()
				return
		if self.tower_selected != None and self.gold > self.tower_selected.cost:
			if self.valid_tile():
				x = self.mouse_x()/self.tile_length
				y = self.mouse_y()/self.tile_length
				self.gold -= self.tower_selected.cost
				self.tiles[x][y] = self.tower_selected(x, y)
				self.tiles[x][y].blocked = True
				self.tiles[x + 1][y].blocked = True
				self.tiles[x][y + 1].blocked = True
				self.tiles[x + 1][y + 1].blocked = True

	def draw(self):
		for tower in self.towers:
			tower.draw(screen)
		for entity in self.entities:
			entity.draw(screen)

	def kill_dead_entities(self):
		i = 0
		while i < len(self.entities):
			if self.entities[i].current_health <= 0:
				self.entities[i].deathrattle()	
				del self.entities[i]
				continue
			i += 1

	def update(self):
		self.kill_dead_entities()
		for tower in self.towers:
			tower.draw(screen)
		for entity in self.entities:
			entity.draw(screen)

if __name__ == '__main__':
	init()
	screen = display.set_mode((1366, 768))
	new_game = TD(screen)