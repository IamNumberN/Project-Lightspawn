from Tile import *

class Spike(Tile):

	def update(self):
		for entity in self.entities:
			entity.health -= 1