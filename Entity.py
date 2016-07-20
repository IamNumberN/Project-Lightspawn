from pygame import *
from math import *
from random import *
from time import *

class Entity:

	def __init__(self, tiles, x, y):
		self.x = x
		self.y = y
		tiles[x/64][y/64].entities.append(self)
		self.color = (randrange(255), randrange(255), randrange(255))
		self.size = 32
		self.rect = Rect(self.x - self.size/2, self.y - self.size/2, self.size, self.size)
		self.max_health = 100
		self.current_health = 100
		self.speed = 10
		self.velocity_weight = 1
		self.velocity_x = 0
		self.velocity_y = 0
		self.separation_weight = 0
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
		self.neighbors = []
		self.neighbor_radius = 32
		self.setup()

	def setup(self):
		self.max_health = 64
		self.current_health = 64

	def normalize(self, vector, constant):
		if sqrt(vector[0]**2 + vector[1]**2) > constant:
			scale = sqrt(vector[0]**2 + vector[1]**2)
			x = vector[0]/scale
			y = vector[1]/scale
			return (constant*x, constant*y)
		else:
			return (0, 0)

	def get_neighbors(self, radius, world_width, world_height, tiles):
		return_lst = []
		for i in range(max(0, self.x/64 - radius), min(world_width, self.x/64 + radius)):
			for j in range(max(0, self.y/64 - radius), min(world_height, self.y/64 + radius)):
				entities = tiles[i][j].entities
				for entity in entities:
					if entity != self and sqrt((self.x - entity.x)**2 + (self.y - entity.y)**2) < radius*64:
						return_lst.append(entity)
		return return_lst

	def darken(self, color, mag):
		return (min(int(mag*color[0]), 255), min(int(mag*color[1]), 255), min(int(mag*color[2]), 255))

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

	def line_of_sight(self, grandparrent, child, tiles):
		x0 = grandparrent.x
		y0 = grandparrent.y
		x1 = child.x
		y1 = child.y
		dy = y1 - y0
		dx = x1 - x0
		f = 0
		if dy < 0:
			dy = -dy
			sy = -1
		else:
			sy = 1
		if dx < 0:
			dx = -dx
			sx = -1
		else:
			sx = 1
		if dx >= dy:
			while x0 != x1:
				f += dy
				if f >= dx:
					if tiles[x0 + ((sx - 1)/2)][y0 + ((sy - 1)/2)].blocked:
						return False
					y0 += sy
					f -= dx
				if f != 0 and tiles[x0 + ((sx - 1)/2)][y0 + ((sy - 1)/2)].blocked:
					return False
				if dy == 0 and tiles[x0 + ((sx - 1)/2)][y0].blocked and tiles[x0 + ((sx - 1)/2)][y0 - 1].blocked:
					return False
				x0 += sx
		else:
			while y0 != y1:
				f += dx
				if f >= dy:
					if tiles[x0 + ((sx - 1)/2)][y0 + ((sy - 1)/2)].blocked:
						return False
					x0 += sx
					f -= dy
				if f != 0 and tiles[x0 + ((sx - 1)/2)][y0 + ((sy - 1)/2)].blocked:
					return False
				if dy == 0 and tiles[x0][y0 + ((sy - 1)/2)].blocked and tiles[x0 - 1][y0 + ((sy - 1)/2)].blocked:
					return False
				y0 += sy
 		return True

	def pathfind(self, start, goal, world_height, world_width, tiles):
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
					new_cost = cost_so_far[current] + len(neighbor.entities)
					cost_so_far[neighbor] = new_cost
					priority = new_cost + self.heuristic(goal, neighbor)
					flag = True
					for i in range(len(frontier)):
						if priority < frontier[i][1]:
							flag = False
							frontier.insert(i, (neighbor, priority))
							if came_from[current] != None and self.line_of_sight(came_from[current], neighbor, tiles):
								came_from[neighbor] = came_from[current]
							else:
								came_from[neighbor] = current
							break
					if flag:
						frontier.insert(len(frontier), (neighbor, priority))
						came_from[neighbor] = current

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
			tile.draw(screen, self.darken(tile.color, 1.1), length)

	def draw_happy(self, screen):
		draw.circle(screen, self.color, (self.x, self.y), self.size/2)

	def draw(self, screen):
		# try:
		# 	direction = self.weighted_angle()
		# 	right_x = self.x + self.size*cos(direction - pi/3)/2
		# 	right_y = self.y + self.size*sin(direction - pi/3)/2
		# 	forward_x = self.x + sqrt(3)*self.size*cos(direction)/2
		# 	forward_y = self.y + sqrt(3)*self.size*sin(direction)/2
		# 	left_x  = self.x + self.size*cos(direction + pi/3)/2
		# 	left_y = self.y + self.size*sin(direction + pi/3)/2
		# 	draw.polygon(screen, self.color, [(right_x, right_y), (forward_x, forward_y), (left_x, left_y)])
		# except:
		# 	pass
		draw.circle(screen, self.color, (self.x, self.y), self.size/2)
		# draw.circle(screen, (255, 255, 255), (self.x, self.y), self.size/4)
		# draw.circle(screen, self.color, (self.x, self.y), self.size/8)
		# rect = (self.x - 3*self.size/8, self.y - 3*self.size/8, 3*self.size/4, 3*self.size/4)	
		# draw.arc(screen, self.darken(self.color, .9), rect, pi/4, 3*pi/4)

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
		#print "velocity", self.velocity_x, self.velocity_y

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
		print "separation", self.separation_x, self.separation_y

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
		print "alignment", self.alignment_x, self.alignment_y

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
		print "cohesion", self.cohesion_x, self.cohesion_y

	def update_location(self):
		self.x += int(self.speed*self.weighted()[0])
		self.y += int(self.speed*self.weighted()[1])

	def update_tiles(self, x, y, length, tiles):
		this_x = (x - self.size/2)/length
		this_y = (y - self.size/2)/length
		# for i in range(this_x, this_x + self.rect.width/length + 1):
		# 	for j in range(this_y, this_y + self.rect.height/length + 1):
		# 		tiles[i][j].blocked = False
		for i in range(len(tiles[this_x][this_y].entities)):
			if tiles[this_x][this_y].entities[i] == self:
				del tiles[this_x][this_y].entities[i]
				break
		world_x = (self.x - self.size/2)/length
		world_y = (self.y - self.size/2)/length
		# for x in range(world_x, world_x + self.rect.width/length + 1):
		# 	for y in range(world_y, world_y + self.rect.height/length + 1):
		# 		tiles[x][y].blocked = True
		tiles[world_x][world_y].entities.append(self)

	def update(self, entities, length, world_width, world_height, tiles):
		x = self.x
		y = self.y
		self.rect = Rect(self.x - self.size/2, self.y - self.size/2, self.size, self.size)
		self.neighbors = self.get_neighbors(self.neighbor_radius, world_width, world_height, tiles)
		self.update_velocity(length)
		self.update_separation()
		self.update_alignment()
		self.update_cohesion()
		self.update_location()
		if self.x/length != x or self.y/length != y:
			self.update_tiles(x, y, length, tiles)