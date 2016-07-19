from pygame import *
from math import *
from Queue import *
from random import *

class Entity:

	def __init__(self, tiles, x, y):
		self.x = x
		self.y = y
		tiles[int(x/64)][int(y/64)].entities.append(self)
		self.color = (randrange(255), randrange(255), randrange(255))
		self.size = 32
		self.rect = Rect(self.x - self.size/2, self.y - self.size/2, self.size, self.size)
		self.max_health = 100
		self.current_health = 100
		self.speed = 1
		self.path_weight = 1
		self.path_angle = None
		self.separation_weight = 0
		self.separation_angle = None
		self.alignment_weight = 0
		self.alignment_angle = None
		self.cohesion_weight = 0
		self.cohesion_angle = None
		self.path = []
		self.buttons = []
		self.neighbors = []
		self.neighbor_radius = 32
		self.setup()

	def normalize(self, vector, constant):
		scale = sqrt(vector[0]**2 + vector[1]**2)
		x = vector[0]/scale
		y = vector[0]/scale
		return (constant*x, constant*y)

	def weighted_angle(self):
		total = 0
		total_weight = 0
		if self.path_angle != None:
			total += self.path_weight*self.path_angle
			total_weight += self.path_weight
		if self.separation_angle != None:
			total += self.separation_weight*self.separation_angle/pi
			total_weight += self.separation_weight
		if self.alignment_angle != None:
			total += self.alignment_weight*self.alignment_angle
			total_weight += self.alignment_weight
		if self.cohesion_angle != None:
			total += self.cohesion_weight*self.cohesion_angle
			total_weight += self.cohesion_weight
		if total_weight != 0:
			return total/total_weight

	def get_neighbors(self, radius, world_width, world_height, tiles):
		return_lst = []
		for i in range(max(0, int(self.x/64 - radius)), min(world_width, int(self.x/64 + radius))):
			for j in range(max(0, int(self.y/64 - radius)), min(world_height, int(self.y/64 + radius))):
				entities = tiles[i][j].entities
				for entity in entities:
					if entity != self and sqrt((self.x - entity.x)**2 + (self.y - entity.y)**2) < radius*64:
						return_lst.append(entity)
		return return_lst

	def heuristic(self, goal, next):
		return sqrt((goal.x - next.x)**2 + (goal.y - next.y)**2)

	def pathfind(self, start, goal, world_height, world_width, tiles):
		frontier = PriorityQueue()
		frontier.put(start, 0)
		came_from = {}
		cost_so_far = {}
		came_from[start] = None
		cost_so_far[start] = 0
		while not frontier.empty():
			current = frontier.get()
			if current == goal:
				self.path = [current]
				while came_from[current] != None:
					current = came_from[current]
					self.path.append(current)
			for neighbor in current.get_neighbors(world_height, world_width, tiles):
				new_cost = cost_so_far[current] + 1
				if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
					cost_so_far[neighbor] = new_cost
					priority = new_cost + self.heuristic(goal, neighbor)
					frontier.put(neighbor, priority)
					came_from[neighbor] = current

	def setup(self):
		self.max_health = 64
		self.current_health = 64
		self.speed = 1

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

	def draw_angles(self, screen):
		start = (self.x, self.y)
		if self.path_angle != None:
			end = (self.x + 50*cos(self.path_angle), self.y + 50*sin(self.path_angle))
			draw.line(screen, (255, 255, 0), start, end)#yellow
		if self.separation_angle != None:
			end = (self.x + 50*cos(self.separation_angle), self.y + 50*sin(self.separation_angle))
			draw.line(screen, (0, 255, 255), start, end)#teal
		if self.alignment_angle != None:
			end = (self.x + 50*cos(self.alignment_angle), self.y + 50*sin(self.alignment_angle))
			draw.line(screen, (255, 0, 255), start, end)#purple
		if self.cohesion_angle != None:
			end = (self.x + 50*cos(self.cohesion_angle), self.y + 50*sin(self.cohesion_angle))
			draw.line(screen, (255, 255, 255), start, end)#white

	def draw_path(self, screen, length, camera_x, camera_y):
		for tile in self.path:
			rect = Rect(length*(tile.x - camera_x/length), length*(tile.y - camera_y/length), length, length)
			draw.rect(screen, self.color, rect)

	def draw(self, screen):
		draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size/2)
		try:
			direction = self.weighted_angle()
			right_x = self.x + self.size*cos(direction - pi/3)/2
			right_y = self.y + self.size*sin(direction - pi/3)/2
			forward_x = self.x + sqrt(3)*self.size*cos(direction)/2
			forward_y = self.y + sqrt(3)*self.size*sin(direction)/2
			left_x  = self.x + self.size*cos(direction + pi/3)/2
			left_y = self.y + self.size*sin(direction + pi/3)/2
			draw.polygon(screen, self.color, [(right_x, right_y), (forward_x, forward_y), (left_x, left_y)])
		except:
			pass

	def update_path_angle(self):
		if self.path != []:
			self.path_angle = atan2((self.path[0].y*64 - self.y), (self.path[0].y*64 - self.x))
		else:
			self.path_angle = None

	def update_separation_angle(self):
		separation_angles = []
		seperation_angles_weights = 0
		self.separation_angle = None
		for entity in self.neighbors:
			if self.path_angle != None:
				adjacent = sqrt((entity.x - self.x)**2 + (entity.y - self.y)**2)
				angle = 2*atan2(entity.size/2, adjacent)
				angle_to_entity = atan2(entity.y - self.y, entity.x - self.x)
				if self.path_angle < angle_to_entity + angle and self.path_angle > angle_to_entity - angle:
					if self.path_angle > angle_to_entity:
						separation_angles.append((angle_to_entity + angle)%(2*pi))
					elif self.path_angle <= angle_to_entity:
						separation_angles.append((angle_to_entity - angle)%(2*pi))
		if separation_angles != []:
			self.separation_angle = sum(separation_angles)/len(separation_angles)

	def update_alignment_angle(self):
		alignment_angles  = []
		self.alignment_angle = None
		for entity in self.neighbors:
			if entity.path_angle != None:
				alignment_angles.append(entity.path_angle)
		if alignment_angles != []:
			self.alignment_angle = sum(alignment_angles)/len(alignment_angles)

	def update_cohesion_angle(self):
		cohesion_x = []
		cohesion_y = []
		self.cohesion_angle = None
		for entity in self.neighbors:
			if entity.path_angle != None:
				cohesion_x.append(entity.x)
				cohesion_y.append(entity.y)
		if cohesion_x != []:
			y = sum(cohesion_y)/len(cohesion_y) - self.y
			x = sum(cohesion_x)/len(cohesion_x) - self.x
			self.cohesion_angle = atan2(y, x)

	def update_location(self):
		if self.path != [] and sqrt((self.path[0].y*64 - self.y)**2 + (self.path[0].x*64 - self.x)**2) < self.speed:
			del self.path[0]
		else:
			try:
				self.x += self.speed*cos(self.weighted_angle())
				self.y += self.speed*sin(self.weighted_angle())
			except:
				pass

	def update_tiles(self, x, y, length, tiles):
		this_x = int((x - self.size/2)/length)
		this_y = int((y - self.size/2)/length)
		for i in range(this_x, this_x + self.rect.width/length + 1):
			for j in range(this_y, this_y + self.rect.height/length + 1):
				tiles[i][j].availability = True
		for i in range(len(tiles[this_x][this_y].entities)):
			if tiles[this_x][this_y].entities[i] == self:
				del tiles[this_x][this_y].entities[i]
				break
		world_x = int((self.x - self.size/2)/length)
		world_y = int((self.y - self.size/2)/length)
		for x in range(world_x, world_x + self.rect.width/length + 1):
			for y in range(world_y, world_y + self.rect.height/length + 1):
				tiles[x][y].availability = False
		tiles[world_x][world_y].entities.append(self)

	def update(self, entities, length, world_width, world_height, tiles):
		x = self.x
		y = self.y
		self.rect = Rect(self.x - self.size/2, self.y - self.size/2, self.size, self.size)
		self.neighbors = self.get_neighbors(self.neighbor_radius, world_width, world_height, tiles)
		self.update_path_angle()
		self.update_separation_angle()
		self.update_alignment_angle()
		self.update_cohesion_angle()
		self.update_location()
		if self.x/length != x or self.y/length != y:
			self.update_tiles(x, y, length, tiles)