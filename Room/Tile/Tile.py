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

	def darken(self, color, mag):
		return (min(int(mag*color[0]), 255), min(int(mag*color[1]), 255), min(int(mag*color[2]), 255))
	
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

