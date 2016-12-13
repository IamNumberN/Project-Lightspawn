from random import *
from pygame import *

class Tile:

	def __init__(self, x, y):
		self.type = 0
		self.seen = True
		self.light_level = 0
		self.blocked = False
		self.level = 1
		self.transparent = True
		self.color = (randrange(232, 242), randrange(196, 206), randrange(170, 180))
		self.x = x
		self.y = y
		self.setup()

	def setup(self):
		pass

	def pix_x(self, length):
		return (self.x + .5)*length

	def pix_y(self, length):
		return (self.y + .5)*length
	
	def get_neighbors(self, world_height, world_width, tiles):
		return_list = []
		if self.y != 0:
			return_list.append(tiles[self.x][self.y - 1])
		if self.y != world_height - 1:
			return_list.append(tiles[self.x][self.y + 1])
		if self.x != 0:
			return_list.append(tiles[self.x - 1][self.y])
		if self.x != world_width - 1:
			return_list.append(tiles[self.x + 1][self.y])
		return return_list

	def draw(self, screen, tile, length, sheet):
		screen.blit(sheet[48], (self.x*length, self.y*length))

	def update(self):
		pass

