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
		self.velocity_weight = 10000
		self.acceleration_x = 0
		self.acceleration_y = 0
		self.velocity_x = 0
		self.velocity_y = 0
		self.separation_weight = 100
		self.separation_x = 0
		self.separation_y = 0
		self.alignment_weight = 1
		self.alignment_x = 0
		self.alignment_y = 0
		self.cohesion_weight = 1
		self.cohesion_x = 0
		self.cohesion_y = 0
		self.path = []
		self.buttons = []
		self.neighbor_radius = 2
		self.light_radius = 6
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
			while self.while_condition(y, length*grandparrent.y, Ya):
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
		if self.line_of_sight(start, goal, tiles, length):
			self.path = [goal]
			return
		frontier = []
		frontier.append((start, 0))
		came_from = {}
		cost_so_far = {}
		came_from[start] = None
		cost_so_far[start] = 0
		while frontier != []:
			current = frontier[0][0]
			frontier.pop(0)
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

	def draw_attack(self, frame):
		pass		

	def draw_line_to_destination(self, screen):
		if len(self.path) > 2:
			for i in range(len(self.path)):
				if i == 0:
					draw.line(screen, (100, 255, 100), (self.x, self.y), self.path[0])
				else:
					draw.line(screen, (100, 255, 100), self.path[i], self.path[i - 1])

	def draw_health(self, screen):
		offset = (self.x - self.size/2 - (self.max_health - self.rect.width)/2, self.y - self.size/2 - 64)
		draw.rect(screen, (0, 0, 0), Rect(offset, (self.max_health, 32)))
		draw.rect(screen, (0, 255, 0), Rect(offset, (self.current_health, 32)))

	def draw_path(self, screen, length):
		for tile in self.path:
			tile.draw(screen, tile.darken(tile.color, 1.1), length)

	def draw_selected(self, screen):
		draw.circle(screen, (0, 255, 0), (self.x, self.y), 2*self.size/3, 1)

	def draw(self, screen):
		draw.circle(screen, self.color, (self.x, self.y), self.size/2)

	def attack(self, frame):
		pass

	def update_velocity(self, length):
		self.velocity_x = 0
		self.velocity_y = 0
		if self.path != []:
			velocity_x = self.path[0].x*length + length/2 - self.x
			velocity_y = self.path[0].y*length + length/2 - self.y
			if sqrt(velocity_x**2 + velocity_y**2) < self.speed:
				self.path.pop(0)
			else:
				self.velocity_x = velocity_x
				self.velocity_y = velocity_y

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

	def update_neighbors(self):
		pass

	def update(self, entities, length, tiles, frame):
		x = self.x
		y = self.y
		self.rect = Rect(self.x - self.size/2, self.y - self.size/2, self.size, self.size)
		self.attack(frame)
		self.neighbors = self.get_neighbors(self.neighbor_radius, len(tiles), len(tiles[0]), tiles, length)
		self.update_velocity(length)
		self.update_separation()
		self.update_alignment()
		self.update_cohesion()
		self.update_location(len(tiles), len(tiles[0]), length)
		if self.x/length != x or self.y/length != y:
			self.update_tiles(x, y, length, tiles)
			self.update_neighbors()