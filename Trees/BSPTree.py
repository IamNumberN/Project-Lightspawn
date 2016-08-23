from random import *

class BSP_Node:

	def __init__(self, x, y, width, height):
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.center_x = self.x + self.width/2
		self.center_y = self.y + self.height/2
		self.direction = None
		self.child1 = None
		self.child2 = None

	def split(self):
		if self.width > 10 and self.height > 10:
			#Choose a random direction : horizontal or vertical splitting
			direction = randrange(2)
			self.direction = direction
			#Split the dungeon into two sub-dungeons
			if direction:
				position = randrange(self.width/2 - 5, self.width/2 + 5)
				self.child1 = BSP_Node(self.x, self.y, position, self.height)
				self.child2 = BSP_Node(self.x + position, self.y, self.width - position, self.height)
			else:
				position = randrange(self.height/2 - 5, self.height/2 + 5)
				self.child1 = BSP_Node(self.x, self.y, self.width, position)
				self.child2 = BSP_Node(self.x, self.y + position, self.width, self.height - position)
			self.child1.split()
			self.child2.split()

	def get_leaves(self):
		if self.child1 == None and self.child2 == None:
			return [self]
		else:
			return self.child1.get_leaves() + self.child2.get_leaves()