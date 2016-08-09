from Room import *
from Tile import *

class Room00(Room):

	def __init__(self):
		self.tiles = [[Wall, Wall, Wall, Wall, Wall, Wall, Wall, Wall, Wall, Wall, Wall, Wall],
				[Tile, Wall, Wall, Wall, Wall, Wall, Wall, Wall, Wall, Wall, Wall, Tile],
				[Tile, Tile, Wall, Wall, Wall, Wall, Wall, Wall, Wall, Wall, Tile, Tile],
				[Tile, Tile, Tile, Wall, Wall, Wall, Wall, Wall, Wall, Tile, Tile, Tile],
				[Tile, Tile, Spike, Tile, Tile, Tile, Tile, Tile, Tile, Tile, Tile, Tile],
				[Tile, Tile, Spike, Tile, Tile, Tile, Tile, Tile, Tile, Tile, Tile, Tile],
				[Tile, Tile, Tile, Wall, Wall, Wall, Wall, Wall, Wall, Tile, Tile, Tile],
				[Tile, Tile, Wall, Wall, Wall, Wall, Wall, Wall, Wall, Wall, Tile, Tile],
				[Tile, Wall, Wall, Wall, Wall, Wall, Wall, Wall, Wall, Wall, Wall, Tile],
				[Wall, Wall, Wall, Wall, Wall, Wall, Wall, Wall, Wall, Wall, Wall, Wall]]