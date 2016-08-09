from Tiles import *

class Wall(Tile):

	def setup(self):
		self.blocked = True
		self.transparent = False
		self.color = (255, 0, 0)