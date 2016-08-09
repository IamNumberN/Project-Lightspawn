from pygame import *
from math import *
from random import *
from time import *

def timer(function, *args):
		start = time()
		ret = function(*args)
		end = time()
		print function.__name__, ":", end - start
		return ret

class Entity:

	def __init__(self, tiles, x, y, length):
		self.x = x
		self.y = y
		tiles[x/length][y/length].entities.append(self)
		self.color = (randrange(255), randrange(255), randrange(255))
		self.size = 32
		self.rect = Rect(self.x - self.size/2, self.y - self.size/2, self.size, self.size)
		self.max_health = 100
		self.current_health = 100

		self.speed = 5
		self.velocity_weight = 100
		self.acceleration_x = 0
		self.acceleration_y = 0
		self.velocity_x = 0
		self.velocity_y = 0
		self.separation_weight = 90
		self.separation_x = 0
		self.separation_y = 0
		self.alignment_weight = 0
		self.alignment_x = 0
		self.alignment_y = 0
		self.cohesion_weight = 0
		self.cohesion_x = 0
		self.cohesion_y = 0
		self.path = []

		self.buttons = []
		self.neighbor_radius = 2
		self.light_radius = 8
		self.attack_radius = 6
		self.side = 0
		self.command_queue = []
		self.update_neighbors(tiles, length)
		self.setup()

	def setup(self):
		pass

	def normalize(self, vector, constant):
		if sqrt(vector[0]**2 + vector[1]**2) > constant:
			scale = sqrt(vector[0]**2 + vector[1]**2)
			x = vector[0]/scale
			y = vector[1]/scale
			return (constant*x, constant*y)
		else:
			return (0, 0)

	def get_neighbors(self, radius, world_width, world_height, tiles, length):
		return_lst = []
		left = max(0, self.x/length - int(ceil(radius)))
		right = min(world_width, self.x/length + int(ceil(radius)))
		top = max(0, self.y/length - int(ceil(radius)))
		bottom = min(world_height, self.y/length + int(ceil(radius)))
		for x in range(left, right):
			for y in range(top, bottom):
				entities = tiles[x][y].entities
				for entity in entities:
					if entity != self and sqrt((self.x - entity.x)**2 + (self.y - entity.y)**2) < radius*length:
						return_lst.append(entity)
		return return_lst

	def weighted(self):
		velocity_x = self.velocity_weight*self.velocity_x
		velocity_y = self.velocity_weight*self.velocity_y
		separation_x = self.separation_weight*self.separation_x
		separation_y = self.separation_weight*self.separation_y
		alignment_x = self.alignment_weight*self.alignment_x
		alignment_y = self.alignment_weight*self.alignment_y
		cohesion_x = self.cohesion_weight*self.cohesion_x
		cohesion_y = self.cohesion_weight*self.cohesion_y
		x = velocity_x + separation_x + alignment_x + cohesion_x
		y = velocity_y + separation_y + alignment_y + cohesion_y
		return self.normalize((x, y), 1)

	def heuristic(self, goal, next):
		return sqrt((goal.x - next.x)**2 + (goal.y - next.y)**2)

	def while_condition(self, var, other_var, direction):
		if direction < 0:
			return var > other_var
		elif direction > 0:
			return var < other_var

	def click_began(self):
		pass

	def line_of_sight(self, grandparrent, child, tiles, length):
		dx = length*(grandparrent.x - child.x)
		dy = length*(grandparrent.y - child.y)
		#verticle intersections
		if dy != 0:
			if dx < 0:
				x = child.x*length + length
			elif dx > 0:
				x = child.x*length - length
			elif dx == 0:
				x = child.x*length
			#pointing up
			if dy < 0:
				y = child.y*length + length
				Ya = -length
			#pointing down
			elif dy > 0:
				y = child.y*length - length
				Ya = length
			while self.while_condition(y, length*grandparrent.y, Ya):#and within screen
				if tiles[int(x/length)][int(y/length)].blocked:
					return False
				y += Ya
				x += float(dx)/dy*Ya
		#horizontal intersections
		if dx != 0:
			if dy < 0:
				y = child.y*length + length
			elif dy > 0:
				y = child.y*length - length
			elif dy == 0:
				y = child.y*length
			#pointing left
			if dx < 0:
				x = child.x*length + length
				Xa = -length
			#pointing right
			elif dx > 0:
				x = child.x*length - length
				Xa = length
			while self.while_condition(x, length*grandparrent.x, Xa):
				if tiles[int(x/length)][int(y/length)].blocked:
					return False
				x += Xa
				y += float(dy)/dx*Xa
		return True

	def pathfind(self, start, goal, world_height, world_width, tiles, length):
		# if self.line_of_sight(start, goal, tiles, length):
		# 	self.path = [goal]
		# 	return
		frontier = []
		frontier.append((start, 0))
		came_from = {}
		cost_so_far = {}
		came_from[start] = None
		cost_so_far[start] = 0
		while frontier != []:
			current = frontier.pop(0)[0]
			if current == goal:
				self.path = [current]
				while came_from[current] != None:
					current = came_from[current]
					self.path.insert(0, current)
				break
			for neighbor in current.get_neighbors(world_height, world_width, tiles):
				if (neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]) and not neighbor.blocked:
					new_cost = cost_so_far[current] + len(neighbor.entities) + 1
					cost_so_far[neighbor] = new_cost
					priority = new_cost + self.heuristic(goal, neighbor)
					flag = True
					for i in range(len(frontier)):
						if priority < frontier[i][1]:
							flag = False
							frontier.insert(i, (neighbor, priority))
							if came_from[current] != None and self.line_of_sight(came_from[current], neighbor, tiles, length):
								came_from[neighbor] = came_from[current]
							else:
								came_from[neighbor] = current
							break
					if flag:
						frontier.insert(len(frontier), (neighbor, priority))
						came_from[neighbor] = current

	def keys(self):
		pass

	def draw_selected(self, screen):
		draw.circle(screen, (0, 255, 0), (self.x, self.y), 2*self.size/3, 1)

	def draw(self, screen):
		draw.circle(screen, self.color, (self.x, self.y), self.size/2)

	def update_velocity(self, length):
		self.velocity_x = 0
		self.velocity_y = 0
		if self.path != []:
			self.velocity_x = self.path[0].x*length - self.x
			self.velocity_y = self.path[0].y*length - self.y

	def update_separation(self):
		self.separation_x = 0
		self.separation_y = 0
		if self.neighbors == []:
			return
		for entity in self.neighbors:
			self.separation_x += self.x - entity.x
			self.separation_y += self.y - entity.y
		self.separation_x /= len(self.neighbors)
		self.separation_y /= len(self.neighbors)

	def update_alignment(self):
		self.alignment_x = 0
		self.alignment_y = 0
		if self.neighbors == []:
			return
		for entity in self.neighbors:
			self.alignment_x += entity.velocity_x
			self.alignment_y += entity.velocity_y
		self.alignment_x /= len(self.neighbors)
		self.alignment_y /= len(self.neighbors)

	def update_cohesion(self):
		self.cohesion_x = 0
		self.cohesion_y = 0
		if self.neighbors == []:
			return
		for entity in self.neighbors:
			self.cohesion_x += entity.x
			self.cohesion_y += entity.y
		self.cohesion_x /= len(self.neighbors)
		self.cohesion_y /= len(self.neighbors)
		self.cohesion_x -= self.x
		self.cohesion_y -= self.y

	def update_location(self, world_width, world_height, length):
		if 0 <= self.x + int(self.speed*self.weighted()[0]) <= world_width*length:
			self.x += int(self.speed*self.weighted()[0])
		if 0 <= self.y + int(self.speed*self.weighted()[1]) <= world_height*length:
			self.y += int(self.speed*self.weighted()[1])

	def update_tiles(self, x, y, length, tiles):
		this_x = (x - self.size/2)/length
		this_y = (y - self.size/2)/length
		for i in range(len(tiles[this_x][this_y].entities)):
			if tiles[this_x][this_y].entities[i] == self:
				del tiles[this_x][this_y].entities[i]
				break
		world_x = (self.x - self.size/2)/length
		world_y = (self.y - self.size/2)/length
		tiles[world_x][world_y].entities.append(self)

	def update_neighbors(self, tiles, length):
		self.neighbors = self.get_neighbors(self.neighbor_radius, len(tiles), len(tiles[0]), tiles, length)

	#if the tile is seen then pathfind to it
	def move(self, frame, tile, tiles, length):
		# if frame%20 == 0:
		# 	self.pathfind(tiles[self.x/length][self.y/length], tile, world_height, world_width, tiles, length)
		if tiles[self.x/length][self.y/length] == tile:
			del self.command_queue[0]
			return
		x = self.x
		y = self.y
		self.rect = Rect(self.x - self.size/2, self.y - self.size/2, self.size, self.size)
		self.update_velocity(length)
		self.update_separation()
		self.update_alignment()
		self.update_cohesion()
		self.update_location(len(tiles), len(tiles[0]), length)
		if self.x/length != x or self.y/length != y:
			self.update_tiles(x, y, length, tiles)
			self.update_neighbors(tiles, length)

	def attack(self, frame, entity):
		pass
		#if the entity is within my FOV if it is within my rnage of attack then attack else do breath first seach for a valid position to attack

	def attack_move(self, frame, entity):
		pass
		#

	def hold(self):
		pass
		#if the entity is within my range of attack then attack

	def patrol(self, frame, tile):
		pass
		#create path from my current tile to the tile parameter if the entity is

	def follow(self, frame, entity):
		pass

	def update(self, entities, length, tiles, frame):
		# x = self.x
		# y = self.y
		# self.rect = Rect(self.x - self.size/2, self.y - self.size/2, self.size, self.size)

		# self.update_velocity(length)
		# self.update_separation()
		# self.update_alignment()
		# self.update_cohesion()
		# self.update_location(len(tiles), len(tiles[0]), length)

		# if self.x/length != x or self.y/length != y:
		# 	self.update_tiles(x, y, length, tiles)
		# 	self.update_neighbors(tiles, length)
		if self.command_queue == []:
			for entity in entities:
				if entity.side != self.side:
					self.command_queue = [(self.attack, (self.frame, entity))]
		else:
			self.command_queue[0][0](*self.command_queue[0][1])