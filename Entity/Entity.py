from pygame import *
from math import *
from random import *
from time import *
from Pause import *

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

	def __init__(self, x, y, side):
		self.x = x
		self.y = y
		self.color = (randrange(255), randrange(255), randrange(255))
		self.size = 32
		self.rect = Rect(self.x - self.size/2, self.y - self.size/2, self.size, self.size)

		self.max_health = 100
		self.current_health = 100
		self.max_energy = 100
		self.current_energy = 100
		self.damage = 15
		self.speed = 10
		self.acceleration = 1
		self.attack_rate = 40
		self.recaluclate_path_rate = 40

		self.acceleration_x = 0
		self.acceleration_y = 0
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

		self.neighbor_radius = 100
		self.neighbors = []
		self.light_radius = 8
		self.attack_radius = 6
		self.side = side
		self.buttons = []
		self.command_queue = []
		self.setup()

	def setup(self):
		pass

	def tile_x(self, length):
		return int(self.x)/length

	def tile_y(self, length):
		return int(self.y)/length

	def normalize_x(self, vector, constant):
		if sqrt(vector[0]**2 + vector[1]**2) > constant:
			scale = sqrt(vector[0]**2 + vector[1]**2)
			return constant*vector[0]/scale
		else:
			return vector[0]

	def normalize_y(self, vector, constant):
		if sqrt(vector[0]**2 + vector[1]**2) > constant:
			scale = sqrt(vector[0]**2 + vector[1]**2)
			return constant*vector[1]/scale
		else:
			return vector[1]

	def heuristic(self, goal, next):
		return sqrt((goal.x - next.x)**2 + (goal.y - next.y)**2)

	def distance(self, start, end):
		return sqrt(start**2 + end**2)

	def distance_to_entity(self, entity):
		return sqrt((self.x - entity.x)**2 + (self.y - entity.y)**2)

	def distance_to_tile(self, tile, length):
		return sqrt(((tile.x + .5)*length - self.x)**2 + ((tile.y + .5)*length - self.y)**2)

	def entity_within_radius(self, entity, radius):
		return self.distance_to_entity(entity) < radius

	def tile_within_radius(self, tile, length, radius):
		return self.distance_to_tile(tile, length) < radius

	def line_of_sight_tile_to_tile(self, start, end, tiles, length):
		if start != end:
			dx = float(start.x - end.x)
			dy = float(start.y - end.y)
			line1_start_x = (start.x + .5)*length + self.normalize_y((dx, dy), self.size/2)
			line1_start_y = (start.y + .5)*length + self.normalize_x((dx, dy), -self.size/2)
			line1_end_x = (end.x + .5)*length + self.normalize_y((dx, dy), self.size/2)
			line1_end_y = (end.y + .5)*length + self.normalize_x((dx, dy), -self.size/2)
			line2_start_x = (start.x + .5)*length + self.normalize_y((dx, dy), -self.size/2)
			line2_start_y = (start.y + .5)*length + self.normalize_x((dx, dy), self.size/2)
			line2_end_x = (end.x + .5)*length + self.normalize_y((dx, dy), -self.size/2)
			line2_end_y = (end.y + .5)*length + self.normalize_x((dx, dy), self.size/2)	
			line1 = self.line_of_sight_point_to_point((line1_start_x, line1_start_y), (line1_end_x, line1_end_y), tiles, length)
			line2 = self.line_of_sight_point_to_point((line2_start_x, line2_start_y), (line2_end_x, line2_end_y), tiles, length)
			return line1 and line2
		else:
			return True

	def line_of_sight_point_to_point(self, start, end, tiles, length):
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
			while sqrt((x0 - x1)**2 + (y0 - y1)**2) > 1:
				if not (0 <= int(x0/length) <= len(tiles) - 1 and 0 <= int(y0/length) <= len(tiles[0]) - 1):
					return True
				if dx < 0 and tiles[int(x0/length)][int(y0/length)].blocked:
					return False
				elif dx > 0 and tiles[int(x0/length) - 1][int(y0/length)].blocked:
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
			while sqrt((x0 - x1)**2 + (y0 - y1)**2) > 1:
				if not (0 <= int(x0/length) <= len(tiles) - 1 and 0 <= int(y0/length) <= len(tiles[0]) - 1):
					return True
				if dy < 0 and tiles[int(x0/length)][int(y0/length)].blocked:
					return False
				elif dy > 0 and tiles[int(x0/length)][int(y0/length) - 1].blocked:
					return False
				y0 += Ya
				x0 += dx/dy*Ya
		return True

	def a_star(self, goal, tiles, length):
		start = tiles[int(self.x)/length][int(self.y)/length]
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
				new_cost = cost_so_far[current] + 1
				if (neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]) and not neighbor.blocked:
					came_from[neighbor] = current
					cost_so_far[neighbor] = new_cost
					priority = new_cost + self.heuristic(goal, neighbor)
					flag = True
					for i in xrange(len(frontier)):
						if priority < frontier[i][1]:
							flag = False
							frontier.insert(i, (neighbor, priority))
							break
					if flag:
						frontier.insert(len(frontier), (neighbor, priority))

	def a_star_with_path_smoothing(self, goal, tiles, length):
		start = tiles[int(self.x)/length][int(self.y)/length]
		if goal.blocked or start.blocked:
			return
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
					if not self.line_of_sight_tile_to_tile(came_from[current], self.path[0], tiles, length):
						self.path.insert(0, current)
					current = came_from[current]
				break
			for neighbor in current.get_neighbors(len(tiles[0]), len(tiles), tiles):
				new_cost = cost_so_far[current] + 1
				if (neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]) and not neighbor.blocked:
					came_from[neighbor] = current
					cost_so_far[neighbor] = new_cost
					priority = new_cost + 1.5*self.heuristic(goal, neighbor)
					flag = True
					for i in xrange(len(frontier)):
						if priority < frontier[i][1]:
							flag = False
							frontier.insert(i, (neighbor, priority))
							break
					if flag:
						frontier.insert(len(frontier), (neighbor, priority))

	def theta_star(self, goal, tiles, length):
		start = tiles[int(self.x)/length][int(self.y)/length]
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
				if came_from[current] != None and self.line_of_sight_tile_to_tile(came_from[current], neighbor, tiles, length):
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
					for i in xrange(len(frontier)):
						if priority < frontier[i][1]:
							flag = False
							frontier.insert(i, (neighbor, priority))
							break
					if flag:
						frontier.insert(len(frontier), (neighbor, priority))

	def lazy_theta_star(self, goal, tiles, length):
		start = tiles[int(self.x)/length][int(self.y)/length]
		frontier = []
		frontier.append((start, 0))
		came_from = {}
		cost_so_far = {}
		came_from[start] = None
		cost_so_far[start] = 0
		while frontier != []:
			current = frontier.pop(0)[0]
			if came_from[current] != None and not self.line_of_sight_tile_to_tile(came_from[current], current, tiles, length):
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
					for i in xrange(len(frontier)):
						if priority < frontier[i][1]:
							flag = False
							frontier.insert(i, (neighbor, priority))
							break
					if flag:
						frontier.insert(len(frontier), (neighbor, priority))

	def keys(self):
		pass

	def draw_line_of_sight_tile_to_tile(self, screen, start, end, tiles, length):
		if start != end:
			dx = float(start.x - end.x)
			dy = float(start.y - end.y)
			line1_start_x = (start.x + .5)*length + self.normalize_y((dx, dy), self.size/2)
			line1_start_y = (start.y + .5)*length + self.normalize_x((dx, dy), -self.size/2)
			line1_end_x = (end.x + .5)*length + self.normalize_y((dx, dy), self.size/2)
			line1_end_y = (end.y + .5)*length + self.normalize_x((dx, dy), -self.size/2)
			line2_start_x = (start.x + .5)*length + self.normalize_y((dx, dy), -self.size/2)
			line2_start_y = (start.y + .5)*length + self.normalize_x((dx, dy), self.size/2)
			line2_end_x = (end.x + .5)*length + self.normalize_y((dx, dy), -self.size/2)
			line2_end_y = (end.y + .5)*length + self.normalize_x((dx, dy), self.size/2)	
			line1 = self.draw_line_of_sight_point_to_point(screen, (line1_start_x, line1_start_y), (line1_end_x, line1_end_y), tiles, length)
			line2 = self.draw_line_of_sight_point_to_point(screen, (line2_start_x, line2_start_y), (line2_end_x, line2_end_y), tiles, length)
			return line1 and line2
		else:
			return True

	def draw_line_of_sight_point_to_point(self, screen, start, end, tiles, length):
		start = (int(start[0]), int(start[1]))
		end = (int(end[0]), int(end[1]))
		draw.line(screen, (0, 0, 255), start, end)
		display.update()
		sleep(.5)
		dx = float(start[0] - end[0])
		dy = float(start[1] - end[1])
		print dx, dy
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
			while sqrt((x0 - x1)**2 + (y0 - y1)**2) > 1:
				draw.circle(screen, (255, 255, 0), (int(x0), int(y0)), 3)
				display.update()
				sleep(.5)
				if not (0 <= int(x0/length) <= len(tiles) - 1 and 0 <= int(y0/length) <= len(tiles[0]) - 1):
					draw.line(screen, (0, 255, 0), start, end)
					display.update()
					sleep(.5)
					return True
				tiles[int(x0/length) - 1][int(y0/length)].draw(screen, (0, 0, 0), length)
				display.update()
				sleep(.5)
				if dx < 0 and tiles[int(x0/length)][int(y0/length)].blocked:
					draw.line(screen, (255, 0, 0), start, end)
					display.update()
					sleep(.5)
					return False
				if dx > 0 and tiles[int(x0/length) - 1][int(y0/length)].blocked:
					print "this"
					draw.line(screen, (255, 0, 0), start, end)
					display.update()
					sleep(.5)
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
			while sqrt((x0 - x1)**2 + (y0 - y1)**2) > 1:
				draw.circle(screen, (0, 255, 255), (int(x0), int(y0)), 3)
				display.update()
				sleep(.5)
				if not (0 <= int(x0/length) <= len(tiles) - 1 and 0 <= int(y0/length) <= len(tiles[0]) - 1):
					draw.line(screen, (0, 255, 0), start, end)
					display.update()
					sleep(.5)
					return True
				tiles[int(x0/length)][int(y0/length) - 1].draw(screen, (0, 0, 0), length)
				display.update()
				sleep(.5)
				if dy < 0 and tiles[int(x0/length)][int(y0/length)].blocked:
					draw.line(screen, (255, 0, 0), start, end)
					display.update()
					sleep(.5)
					return False
				if dy > 0 and tiles[int(x0/length)][int(y0/length) - 1].blocked:
					print "this"
					draw.line(screen, (255, 0, 0), start, end)
					display.update()
					sleep(.5)
					return False
				y0 += Ya
				x0 += dx/dy*Ya
		draw.line(screen, (0, 255, 0), start, end)
		display.update()
		sleep(.5)
		return True

	def draw_selected(self, screen):
		rect = Rect(self.x - 2*self.size/3, self.y - 2*self.size/3, 4*self.size/3, 4*self.size/3)
		draw.arc(screen, (0, 255, 0), rect, pi/2 - float(self.current_health)/self.max_health*pi, pi/2 + float(self.current_health)/self.max_health*pi, 1)

	def draw(self, screen):
		draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size/2)
		draw.line(screen, (255, 255, 0), (self.x, self.y), (self.x + 3*self.acceleration_x, self.y + 3*self.acceleration_y))
		draw.line(screen, (0, 255, 255), (self.x, self.y), (self.x + 3*self.velocity_x, self.y + 3*self.velocity_y))

	def update_neighbors(self, entities):
		self.neighbors = [entity for entity in entities if self.entity_within_radius(entity, self.neighbor_radius)]

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

	def update_acceleration(self, length):
		separation_x = self.separation_weight*self.separation_x
		separation_y = self.separation_weight*self.separation_y
		alignment_x = self.alignment_weight*self.alignment_x
		alignment_y = self.alignment_weight*self.alignment_y
		cohesion_x = self.cohesion_weight*self.cohesion_x
		cohesion_y = self.cohesion_weight*self.cohesion_y
		self.acceleration_x = separation_x + alignment_x + cohesion_x
		self.acceleration_y = separation_y + alignment_y + cohesion_y
		if len(self.path) == 1 and self.tile_within_radius(self.path[0], length, self.speed/self.acceleration):
			if sqrt(self.velocity_x**2 + self.velocity_y**2) > .1:
				self.acceleration_x += self.normalize_x((self.x - (self.path[0].x + .5)*length, self.y - (self.path[0].y + .5)*length), .1)
				self.acceleration_y += self.normalize_y((self.x - (self.path[0].x + .5)*length, self.y - (self.path[0].y + .5)*length), .1)
		else:
			self.acceleration_x += self.normalize_x((self.x - (self.path[0].x + .5)*length, self.y - (self.path[0].y + .5)*length), -1)
			self.acceleration_y += self.normalize_y((self.x - (self.path[0].x + .5)*length, self.y - (self.path[0].y + .5)*length), -1)
		# print self.velocity_x, self.velocity_y, self.acceleration_x, self.acceleration_y

	def update_forces(self, length):
		self.update_separation()
		self.update_alignment()
		self.update_cohesion()
		self.update_acceleration(length)

	def update_velocity(self):
		self.velocity_x = self.normalize_x((self.velocity_x + self.acceleration_x, self.velocity_y + self.acceleration_y), self.speed)
		self.velocity_y = self.normalize_y((self.velocity_x + self.acceleration_x, self.velocity_y + self.acceleration_y), self.speed)
		#print self.velocity_x, self.velocity_y

	def update_location(self, world_width, world_height, length):
		#if updating doesn't move it into a blocked tile or out of xrange
		if 0 <= self.x + self.velocity_x <= world_width*length:
			self.x += self.velocity_x
		if 0 <= self.y + self.velocity_y <= world_height*length:
			self.y += self.velocity_y
		self.rect = Rect(self.x - self.size/2, self.y - self.size/2, self.size, self.size)

	def move(self, side_1, side_2, current_frame, tiles, length, frame, tile):
		#recaluclate path every 1.33 seconds
		if current_frame%self.recaluclate_path_rate == frame%self.recaluclate_path_rate: 
			self.a_star_with_path_smoothing(tile, tiles, length)
		#if path is empty pop move from command queue
		if self.path == []:
			self.acceleration_x = 0
			self.acceleration_y = 0
			del self.command_queue[0]
			if self.command_queue != []:
				self.command_queue[0] = (self.command_queue[0][0], (current_frame + 1, self.command_queue[0][1][1]))
			return
		#on first run clear everything
		if current_frame == frame:
			self.acceleration_x = 0
			self.acceleration_y = 0
			self.velocity_x = self.normalize_x((self.x - (self.path[0].x + .5)*length, self.y - (self.path[0].y + .5)*length), -self.speed)
			self.velocity_y = self.normalize_y((self.x - (self.path[0].x + .5)*length, self.y - (self.path[0].y + .5)*length), -self.speed)
		#update neighbors, acceleration, velocity, location
		self.update_neighbors(side_1)
		self.update_forces(length)
		self.update_velocity()
		self.update_location(len(tiles), len(tiles[0]), length)
		#if we reach destination then delete it from path set acceleration and velocity to 0
		if self.tile_within_radius(self.path[0], length, self.speed):
			del self.path[0]
			if self.path != []:
				self.velocity_x = self.normalize_x((self.x - (self.path[0].x + .5)*length, self.y - (self.path[0].y + .5)*length), -self.speed)
				self.velocity_y = self.normalize_y((self.x - (self.path[0].x + .5)*length, self.y - (self.path[0].y + .5)*length), -self.speed)

	def attack(self, side_1, side_2, current_frame, tiles, length, frame, entity):
		#if enemy is in xrange stop moving and attack
		if self.entity_within_radius(entity, self.attack_radius) and current_frame%self.attack_rate == frame%self.attack_rate:
			self.acceleration_x = 0
			self.acceleration_y = 0
			self.velocity_x = 0
			self.velocity_y = 0
			entity.current_health -= self.damage
		#if enemy is out of range head towards it
		elif not self.entity_within_radius(entity, self.attack_radius) and self.entity_within_radius(entity, self.light_radius):
			self.move(side_1, side_2, current_frame, tiles, length, frame, entity.tile())
		#if enemy is killed or if enemy is out of sight stop
		elif not self.entity_within_radius(entity, self.light_radius) or entity not in side_2:
			del self.command_queue[0]
			if self.command_queue != []:
				self.command_queue[0] = (self.command_queue[0][0], (current_frame + 1, self.command_queue[0][1][1]))

	def attack_move(self, side_1, side_2, current_frame, tiles, length, frame, tile):
		if self.tile() == tile:
			del self.command_queue[0]
			if self.command_queue != []:
				self.command_queue[0] = (self.command_queue[0][0], (current_frame + 1, self.command_queue[0][1][1]))
			return
		flag = True
		for entity in side_1 + side_2:
			if self.entity_within_radius(entity, self.attack_radius) and entity.side != self.side:
				flag = False
				self.command_queue.insert(0, (self.attack, (frame, entity)))
		if flag:
			self.move(side_1, side_2, current_frame, tiles, length, frame, tile)
	
	def stop(self):
		self.path = []
		self.command_queue = []

	def pause(self, side_1, side_2, current_frame, tiles, length, frame, duration):
		if current_frame - frame == duration:
			del self.command_queue[0]
			if self.command_queue != []:
				self.command_queue[0] = (self.command_queue[0][0], (current_frame + 1, self.command_queue[0][1][1]))
		#stop moving and attacking for number of frames then pop from command queue

	def hold(self):
		pass
		#if enemy is in xrange attack

	def patrol(self, side_1, side_2, current_frame, tiles, length, frame, start, end):
		self.command_queue.insert(0, (self.attack_move, (frame, start)))
		self.command_queue.insert(0, (self.attack_move, (frame, end)))

	def follow(self, frame, entity):
		pass

	def update(self, side_1, side_2, frame, tiles, length):
		if self.command_queue == []:
			for entity in side_1 + side_2:
				if self.entity_within_radius(entity, self.attack_radius) and entity.side != self.side:
					self.command_queue = [(self.attack, (frame, entity))]
		else:
			self.command_queue[0][0](side_1, side_2, frame, tiles, length, *self.command_queue[0][1])