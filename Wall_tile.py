from Tiles import *

class Wall(Tile):

	def setup(self):
		self.blocked = True
		self.color = (randrange(242, 252), randrange(206, 216), randrange(180, 190))