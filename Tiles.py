from random import *
from pygame import *

class Tile:

	def __init__(self, x, y, game):
		self.availability = True
		self.entities = []
		self.color = (randrange(232, 242), randrange(196, 206), randrange(170, 180))
		self.x = x
		self.y = y
		self.game = game
	
	def get_neighbors(self):
		return_list = []
		if self.y != 0:
			return_list.append(self.game.tiles[self.x][self.y - 1])
		if self.y != self.game.world_height - 1:
			return_list.append(self.game.tiles[self.x][self.y + 1])
		if self.x != 0:
			return_list.append(self.game.tiles[self.x - 1][self.y])
		if self.x != self.game.world_width - 1:
			return_list.append(self.game.tiles[self.x + 1][self.y])
		return return_list

	def draw(self, color):
		rect = Rect(self.x*self.game.tile_length, self.y*self.game.tile_length, self.game.tile_length, self.game.tile_length)
		draw.rect(self.game.world, color, rect)

