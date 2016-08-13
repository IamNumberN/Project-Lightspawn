from pygame import *
from math import *
from random import *
from time import *
from Pause import *

blue = (0, 0, 255)
red = (255, 0, 0)
green = (0, 255, 0)

def rando():
	return (randrange(255), randrange(255), randrange(255))

def timer(function, *args):
		start = time()
		ret = function(*args)
		end = time()
		print function.__name__, ":", end - start
		return ret

def stop_until_click():
	run = True
	while run:
		for evnt in event.get():
			if evnt.type == MOUSEBUTTONDOWN:
				run = False
			if evnt.type == QUIT:
				import sys
				sys.exit()

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
		self.max_energy = 100
		self.current_energy = 100

		self.speed = 5
		self.velocity_weight = 100
		self.acceleration_x = 0
		self.acceleration_y = 0
		self.velocity_x = 0
		self.velocity_y = 0
		self.separation_weight = 80
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

		self.pathfind_queue = []
		self.lighting_queue = []

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

	def distance(self, start, end):
		return sqrt(start**2 + end**2)

	def click_began(self):
		pass

	def line_of_sight_tile_to_tile(self, screen, start, end, tiles, length):
		if start != end:
			dx = float(start.x - end.x)
			dy = float(start.y - end.y)
			line1_start_x = (start.x + .5)*length + self.size/2*dy/self.distance(dx, dy)#use self.normalize
			line1_start_y = (start.y + .5)*length - self.size/2*dx/self.distance(dx, dy)
			line1_end_x = (end.x + .5)*length + self.size/2*dy/self.distance(dx, dy)
			line1_end_y = (end.y + .5)*length - self.size/2*dx/self.distance(dx, dy)
			line2_start_x = (start.x + .5)*length - self.size/2*dy/self.distance(dx, dy)
			line2_start_y = (start.y + .5)*length + self.size/2*dx/self.distance(dx, dy)
			line2_end_x = (end.x + .5)*length - self.size/2*dy/self.distance(dx, dy)
			line2_end_y = (end.y + .5)*length + self.size/2*dx/self.distance(dx, dy)	
			line1 = self.line_of_sight_point_to_point(screen, (line1_start_x, line1_start_y), (line1_end_x, line1_end_y), tiles, length)
			line2 = self.line_of_sight_point_to_point(screen, (line2_start_x, line2_start_y), (line2_end_x, line2_end_y), tiles, length)
			return line1 and line2
		else:
			return True

	def line_of_sight_point_to_point(self, screen, start, end, tiles, length):
		start = (int(start[0]), int(start[1]))
		end = (int(end[0]), int(end[1]))
		dx = float(start[0] - end[0])
		dy = float(start[1] - end[1])
		#if line is not pointing up then there are intersections with verticle lines
		if dx != 0:
			#calculate first and last intersection
			if dx < 0:#if point is to the right of entity then
				x0 = (start[0]/length + 1)*length
				x1 = (end[0]/length + 1)*length
				Xa = length
			if dx > 0:#if point is to the left of entity then
				x0 = (start[0]/length)*length
				x1 = (end[0]/length)*length
				Xa = -length
			y0 = start[1] + dy/dx*(x0 - start[0])
			y1 = end[1] + dy/dx*(x1 - end[0])
			while abs(x0 - x1) > .00001 and abs(y0 - y1) > .00001:
				if tiles[int(x0/length)][int(y0/length)].blocked:
					return False
				x0 += Xa
				y0 += dy/dx*Xa
		if dy != 0:
			if dy < 0:
				y0 = (start[1]/length + 1)*length
				y1 = (end[1]/length + 1)*length
				Ya = length
			if dy > 0:
				y0 = (start[1]/length)*length
				y1 = (end[1]/length)*length
				Ya = -length
			x0 = start[0] + dx/dy*(y0 - start[1])
			x1 = end[0] + dx/dy*(y1 - end[1])
			while abs(x0 - x1) > .00001 and abs(y0 - y1) > .00001:
				if tiles[int(x0/length)][int(y0/length)].blocked:
					return False
				y0 += Ya
				x0 += dx/dy*Ya
		return True

	def a_star(self, screen, goal, tiles, length):
		start = tiles[self.x/length][self.y/length]
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
			for neighbor in current.get_neighbors(len(tiles[0]), len(tiles), tiles):
				# neighbor.draw(screen, red, length)
				# display.update()
				new_cost = cost_so_far[current] + 1
				if (neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]) and not neighbor.blocked:
					came_from[neighbor] = current
					cost_so_far[neighbor] = new_cost
					priority = new_cost + self.heuristic(goal, neighbor)
					flag = True
					for i in range(len(frontier)):
						if priority < frontier[i][1]:
							flag = False
							frontier.insert(i, (neighbor, priority))
							break
					if flag:
						frontier.insert(len(frontier), (neighbor, priority))

	def theta_star(self, screen, goal, tiles, length):
		start = tiles[self.x/length][self.y/length]
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
			for neighbor in current.get_neighbors(len(tiles[0]), len(tiles), tiles):
				# neighbor.draw(screen, red, length)
				# display.update()
				if came_from[current] != None and self.line_of_sight_tile_to_tile(screen, came_from[current], neighbor, tiles, length):
					new_cost = cost_so_far[came_from[current]] + self.heuristic(came_from[current], neighbor)
					if (neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]) and not neighbor.blocked:
						came_from[neighbor] = came_from[current]
				else:
					new_cost = cost_so_far[current] + 1
					if (neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]) and not neighbor.blocked:
						came_from[neighbor] = current
				if (neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]) and not neighbor.blocked:
					cost_so_far[neighbor] = new_cost
					priority = new_cost + self.heuristic(goal, neighbor)
					flag = True
					for i in range(len(frontier)):
						if priority < frontier[i][1]:
							flag = False
							frontier.insert(i, (neighbor, priority))
							break
					if flag:
						frontier.insert(len(frontier), (neighbor, priority))

	def lazy_theta_star(self, screen, goal, tiles, length):
		start = tiles[self.x/length][self.y/length]
		frontier = []
		frontier.append((start, 0))
		came_from = {}
		cost_so_far = {}
		came_from[start] = None
		cost_so_far[start] = 0
		while frontier != []:
			current = frontier.pop(0)[0]
			if came_from[current] != None and not self.line_of_sight_tile_to_tile(screen, came_from[current], current, tiles, length):
				neighbors = current.get_neighbors(len(tiles[0]), len(tiles), tiles)
				valid_costs = [cost_so_far[neighbor] for neighbor in neighbors if neighbor in cost_so_far]
				valid_neighbors = [neighbor for neighbor in neighbors if neighbor in cost_so_far]
				smallest = valid_costs.index(min(valid_costs))
				came_from[current] = valid_neighbors[smallest]
				cost_so_far[current] = cost_so_far[valid_neighbors[smallest]] + 1
			if current == goal:
				self.path = [current]
				while came_from[current] != None:
					current = came_from[current]
					self.path.insert(0, current)
				break
			for neighbor in current.get_neighbors(len(tiles[0]), len(tiles), tiles):
				if came_from[current] != None:
					new_cost = cost_so_far[came_from[current]] + self.heuristic(came_from[current], neighbor)
					if (neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]) and not neighbor.blocked:
						came_from[neighbor] = came_from[current]
				else:
					new_cost = 1
					came_from[neighbor] = current
				if (neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]) and not neighbor.blocked:
					cost_so_far[neighbor] = new_cost
					priority = new_cost + self.heuristic(goal, neighbor)
					flag = True
					for i in range(len(frontier)):
						if priority < frontier[i][1]:
							flag = False
							frontier.insert(i, (neighbor, priority))
							break
					if flag:
						frontier.insert(len(frontier), (neighbor, priority))

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
			if sqrt(((self.path[0].x + .5)*length - self.x)**2 + ((self.path[0].y + .5)*length - self.y)**2) < self.speed:
				del self.path[0]
			if self.path != []:
				self.velocity_x = (self.path[0].x + .5)*length - self.x
				self.velocity_y = (self.path[0].y + .5)*length - self.y

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
	
	def stop(self):
		self.path = []

	def hold(self):
		pass
		#if the entity is within my range of attack then attack

	def patrol(self, frame, tile):
		pass
		#create path from my current tile to the tile parameter if the entity is

	def follow(self, frame, entity):
		pass

	def update(self, entities, length, tiles, frame):
		# if self.command_queue == []:
		# 	for entity in entities:
		# 		if entity.side != self.side and self.distance(self, entity) < self.attack_radius:
		# 			self.command_queue = [(self.attack, (self.frame, entity))]
		# else:
		# 	self.command_queue[0][0](*self.command_queue[0][1])

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