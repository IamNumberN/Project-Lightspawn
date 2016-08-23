from Tile import *

class Wall(Tile):

	def setup(self):
		self.blocked = True
		self.transparent = False
		self.mapping = { 2 : 1, 8 : 2, 10 : 3, 11 : 4, 16 : 5, 18 : 6, 22 : 7, 24 : 8, 26 : 9, 27 : 10, 30 : 11, 31 : 12, 64 : 13, 66 : 14, 72 : 15, 74 : 16, 75 : 17, 80 : 18, 82 : 19, 86 : 20, 88 : 21, 90 : 22, 91 : 23, 94 : 24, 95 : 25, 104 : 26, 106 : 27, 107 : 28, 120 : 29, 122 : 30, 123 : 31, 126 : 32, 127 : 33, 208 : 34, 210 : 35, 214 : 36, 216 : 37, 218 : 38, 219 : 39, 222 : 40, 223 : 41, 248 : 42, 250 : 43, 251 : 44, 254 : 45, 255 : 46, 0 : 47 }

	def draw(self, screen, tiles, length, sheet):
		key = 0
		if self.y != 0 and isinstance(tiles[self.x][self.y - 1], Wall):
			key += 2
		if self.y != len(tiles[0]) - 1 and isinstance(tiles[self.x][self.y + 1], Wall):
			key += 64
		if self.x != 0 and isinstance(tiles[self.x - 1][self.y], Wall):
			key += 8
		if self.x != len(tiles) - 1 and isinstance(tiles[self.x + 1][self.y], Wall):
			key += 16
		if self.y != 0  and self.x != 0 and isinstance(tiles[self.x][self.y - 1], Wall) and isinstance(tiles[self.x - 1][self.y], Wall) and isinstance(tiles[self.x - 1][self.y - 1], Wall):
			key += 1
		if self.y != 0 and self.x != len(tiles) - 1 and isinstance(tiles[self.x][self.y - 1], Wall) and isinstance(tiles[self.x + 1][self.y], Wall) and isinstance(tiles[self.x + 1][self.y - 1], Wall):
			key += 4
		if self.x != 0 and self.y != len(tiles[0]) - 1 and isinstance(tiles[self.x][self.y + 1], Wall) and isinstance(tiles[self.x - 1][self.y], Wall)  and isinstance(tiles[self.x - 1][self.y + 1], Wall):
			key += 32
		if self.x != len(tiles) - 1 and self.y != len(tiles[0]) - 1 and isinstance(tiles[self.x][self.y + 1], Wall) and isinstance(tiles[self.x + 1][self.y], Wall) and isinstance(tiles[self.x + 1][self.y + 1], Wall):
			key += 128
		screen.blit(sheet[self.mapping[key]], (self.x*length, self.y*length))