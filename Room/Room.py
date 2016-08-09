class Room:

	def __init__(self):
		self.tiles = [[Tiles(x, y) for y in range(12)] for x in range(10)]