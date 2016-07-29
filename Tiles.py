from random import *
from pygame import *

class Tile:

	def __init__(self, x, y):
		self.type = 0
		self.seen = False
		self.blocked = False
		self.entities = []
		self.color = (randrange(232, 242), randrange(196, 206), randrange(170, 180))
		self.x = x
		self.y = y
		self.setup()

	def setup(self):
		pass
	
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
		if self.y != 0 and self.x != 0:
			return_list.append(tiles[self.x - 1][self.y - 1])
		if self.y != 0 and self.x != world_width - 1:
			return_list.append(tiles[self.x + 1][self.y - 1])
		if self.y != world_height - 1 and self.x != 0:
			return_list.append(tiles[self.x - 1][self.y + 1])
		if self.y != world_height - 1 and self.x != world_width - 1:
			return_list.append(tiles[self.x + 1][self.y + 1])
		return return_list

	def draw(self, screen, color, length):
		rect = Rect(self.x*length, self.y*length, length, length)
		draw.rect(screen, color, rect)

	def update(self):
		print "hi"

