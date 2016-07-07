from pygame import *
from pygame.locals import *
from sys import *
from time import *
from math import *
from random import *
import csv

def change_state(delete, create):
	del delete
	new = create()

class State():

	def __init__(self):
		self.last_right_click = mouse.get_pressed()[0]
		self.last_pos = mouse.get_pos()
		self.last_time = time()
		self.minimized = False
		self.count = 0
		self.setup()
		self.handle_update()

	def setup(self):
		pass

	def click_began(self):
		pass

	def right_click_began(self):
		pass

	def mouse_moved(self):
		pass

	def click_ended(self):
		pass

	def right_click_ended(self):
		pass

	def minimize(self):
		self.minimized = True
		while self.minimized:
			self.handle_events()

	def maximize(self):
		self.minimized = False

	def update(self):
		pass

	def stop(self):
		exit()

	def resize(self):
		pass

	def draw(self):
		display.update()

	def tick(self, fps = 60):
		interval = 1./fps
		delta = time() - self.last_time
		if delta < interval:
			sleep(interval - delta)
		else:
			self.count += 1
			#print "lagging", self.count
		self.last_time = time()

	def present_other_scene(self, other_scene):
		self.other_scene = other_scene()

	def dismiss_other_scene(self):
		del self

	def handle_events(self):
		for evnt in event.get():
			if evnt.type == QUIT:
				self.stop()
			if evnt.type == VIDEORESIZE:
				self.resize()
			if evnt.type == MOUSEBUTTONDOWN:
				if evnt.button == 1:
					self.click_began()
				if evnt.button == 3:
					self.right_click_began()
			if evnt.type == MOUSEBUTTONUP:
				if evnt.button == 1:
					self.click_ended()
				if evnt.button == 3:
					self.right_click_ended()
			if evnt.type == MOUSEMOTION:
				self.mouse_moved()
			if evnt.type == ACTIVEEVENT:
				if evnt.state == 2 and evnt.gain == 0:
					self.minimize()
				if evnt.state == 2 and evnt.gain == 1:
					self.maximize()

	def handle_draw(self):
		screen.fill((0, 0, 0))
		self.draw()

	def handle_update(self):
		while True:
			a = time()
			self.handle_events()
			b = time()
			self.update()
			c = time()
			self.handle_draw()
			d = time()
			self.tick()	
			# with open("data.csv", "a") as csvfile:
			# 	writer = csv.writer(csvfile)
			# 	writer.writerow([c-b])
			# print "handle events:", b - a, "update:", c - b, "draw:", d - c

class Entity:

	def __init__(self, game, x, y):
		self.game = game
		self.x = x
		self.y = y
		self.game.entity_map[int(x/64)][int(y/64)].append(self)
		self.color = (0, 0, 0)
		self.size = 32
		self.rect = Rect(self.x - self.size/2, self.y - self.size/2, self.size, self.size)
		self.max_health = 100
		self.current_health = 100
		self.speed = 1
		self.path_weight = 100
		self.path_angle = None
		self.seperation_weight = 1000
		self.seperation_angle = None
		self.alignment_weight = 1
		self.alignment_angle = None
		self.cohesion_weight = 1
		self.cohesion_angle = None
		self.path = []
		self.buttons = []
		self.neighbors = []
		self.neighbor_radius = 20
		self.setup()

	def weighted_angle(self):
		total = 0
		total_weight = 0
		if self.path_angle != None:
			total += self.path_weight*self.path_angle
			total_weight += self.path_weight
		if self.seperation_angle != None:
			total += self.seperation_weight*self.seperation_angle
			total_weight += self.seperation_weight
		if self.alignment_angle != None:
			total += self.alignment_weight*self.alignment_angle
			total_weight += self.alignment_weight
		if self.cohesion_angle != None:
			total += self.cohesion_weight*self.cohesion_angle
			total_weight += self.cohesion_weight
		return total/total_weight

	def get_neighbors(self, radius):
		return_lst = []
		for i in range(max(0, int(self.x/64 - radius)), min(self.game.world_width, int(self.x/64 + radius))):
			for j in range(max(0, int(self.y/64 - radius)), min(self.game.world_height, int(self.y/64 + radius))):
				entities = self.game.entity_map[i][j]
				for entity in entities:
					if entity != self and sqrt((self.x - entity.x)**2 + (self.y - entity.y)**2) < radius*64:
						return_lst.append(entity)
		return return_lst

	def mark_unavailable(self):
		world_x = int(self.x/self.game.tile_length)
		world_y = int(self.y/self.game.tile_length)
		for x in range(world_x, world_x + self.rect.width/self.game.tile_length + 1):
			for y in range(world_y, world_y + self.rect.height/self.game.tile_length + 1):
				self.game.world_available[x][y] = True

	def mark_available(self):
		world_x = int(self.x/self.game.tile_length)
		world_y = int(self.y/self.game.tile_length)
		for x in range(world_x, world_x + self.rect.width/self.game.tile_length + 1):
			for y in range(world_y, world_y + self.rect.height/self.game.tile_length + 1):
				self.game.world_available[x][y] = False

	def pathfind(self, destination):
		self.path.append(destination)

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
		if self.seperation_angle != None:
			end = (self.x + 50*cos(self.seperation_angle), self.y + 50*sin(self.seperation_angle))
			draw.line(screen, (0, 255, 255), start, end)#teal
		if self.alignment_angle != None:
			end = (self.x + 50*cos(self.alignment_angle), self.y + 50*sin(self.alignment_angle))
			draw.line(screen, (255, 0, 255), start, end)#purple
		if self.cohesion_angle != None:
			end = (self.x + 50*cos(self.cohesion_angle), self.y + 50*sin(self.cohesion_angle))
			draw.line(screen, (255, 255, 255), start, end)#white

	def remove_self_from_entity_map(self):
		for i in range(len(self.game.entity_map[int(self.x/64)][int(self.y/64)])):
			if self.game.entity_map[int(self.x/64)][int(self.y/64)][i] == self:
				del self.game.entity_map[int(self.x/64)][int(self.y/64)][i]
				break

	def update_path_angle(self):
		try:
			self.path_angle = atan2((self.path[0][1] - self.y), (self.path[0][0] - self.x))
		except:
			self.path_angle = None


	def update_seperation_angle(self):
		try:
			seperation_angles = []
			self.seperation_angle = None
			for entity in self.neighbors:
				try:
					magnitude = sqrt((entity.x - self.x)**2 + (entity.y - self.y)**2)
					angle = self.path_angle - atan2(entity.y. entity.x)
					seperation_angle = 1/(magnitude*cos(angle))
					if seperation_angle > pi/2:
						seperation_angle = pi/2
					elif seperation_angle < -pi/2:
						seperation_angle = -pi/2
					seperation_angles.append((self.seperation_angle + path_angle)%(2*pi))
				except:
					seperation_angles.append((pi/2 + self.path_angle)%(2*pi))
				self.seperation_angle = sum(seperation_angles)/len(seperation_angles)
		except:
			self.seperation_angle = None

	def update_alignment_angle(self):
		try:
			self.alignment_angle = sum(entity.path_angle for entity in self.neighbors if entity.path_angle != None)/len(self.neighbors)
		except:
			self.alignment_angle = None

	def update_cohesion_angle(self):
		try:
			cohesion_x = sum(entity.x for entity in self.neighbors if entity.path_angle != None)/len(self.neighbors)
			cohesion_y = sum(entity.y for entity in self.neighbors if entity.path_angle != None)/len(self.neighbors)
			self.cohesion_angle = atan2((cohesion_y - self.y), (cohesion_x - self.x))
		except:
			self.cohesion_angle = None

	def update_location(self):
		try:
			self.x += self.speed*cos(self.weighted_angle())
			self.y += self.speed*sin(self.weighted_angle())
		except:
			pass

	def place_self_on_entity_map(self):
		self.game.entity_map[int(self.x/64)][int(self.y/64)].append(self)

	def check_stop(self):
		if self.path != [] and sqrt((self.path[0][1] - self.y)**2 + (self.path[0][0] - self.x)**2) < self.speed:
			del self.path[0]

	def setup(self):
		pass

	def draw(self, screen, camera_pos):
		pass

	def update(self, entities):
		pass

class Marine(Entity):

	def setup(self):
		self.color = (100, 100, 255)
		self.max_health = 64
		self.current_health = 64
		self.speed = 1

	def draw(self, screen):
		draw.circle(screen, self.color, (int(self.x), int(self.y)), self.rect.width/2)
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

	def update(self, entities):
		self.mark_unavailable()
		self.remove_self_from_entity_map()
		self.rect = Rect(self.x - self.size/2, self.y - self.size/2, self.size, self.size)
		self.neighbors = self.get_neighbors(self.neighbor_radius)
		self.update_path_angle()
		self.update_seperation_angle()
		self.update_alignment_angle()
		self.update_cohesion_angle()
		#print self.path_angle, self.seperation_angle, self.alignment_angle, self.cohesion_angle
		self.update_location()
		self.check_stop()
		self.mark_available()
		self.place_self_on_entity_map()

class Button:

	def __init__(self, action, x, y):
		self.action = action
		self.rect = Rect(x, y, 64, 64)
		self.color = (200, 200, 200)

	def draw(self, color):
		draw.rect(screen, color, self.rect)

class GameState(State):

	def setup(self):
		self.world_width = 200
		self.world_height = 200
		self.tile_length = 64
		self.world = Surface((self.world_width*self.tile_length, self.world_height*self.tile_length))
		self.world_available = [[True for x in range(self.world_height)] for y in range(self.world_width)]
		self.entity_map = [[[] for x in range(self.world_height)] for y in range(self.world_width)]
		self.world_image = self.generate_world_image(self.world_width, self.world_height, self.tile_length)
		self.world.blit(self.world_image, (0, 0))
		self.buttons = []
		self.entities = [Marine(self, 128*i, 128*i) for i in range(1, 99)]
		self.selection = None
		self.click_x = None
		self.click_y = None
		self.selection_box = None
		self.entities_selected = self.entities
		self.camera_x = 0
		self.camera_y = 0
		self.show_grid = False
		self.show_world_available = False
		self.font = font.Font(None, 24)

	def show_grid(self):
		self.show_grid = not self.show_grid

	def mouse_x(self):
		return mouse.get_pos()[0]

	def mouse_y(self):
		return mouse.get_pos()[1] 

	def camera_mouse(self):
		return self.mouse_x() - self.camera_x, self.mouse_y() - self.camera_y

	def camera_mouse_x(self):
		return self.mouse_x() - self.camera_x

	def camera_mouse_y(self):
		return self.mouse_y() - self.camera_y

	def generate_world_image(self, width, height, length):
		surface = Surface((width*length, height*length))
		rect = Rect(0, 0, length, length)
		for x in range(width):
			for y in range(height):
				rect.topleft = x*length, y*length
				color = (randrange(232, 242), randrange(196, 206), randrange(170, 180))
				draw.rect(surface, color, rect)
		return surface

	def click_began(self):
		flag = True
		#detect button click
		for button in self.buttons:
			if button.rect.collidepoint(mouse.get_pos()):
				button.action()
				flag = False
		#detect entity click
		for entity in self.entities:
			if entity.rect.collidepoint(self.camera_mouse()) and entity != self.selection:
				self.entities_selected = [entity]
				flag = False
		#if clicking on nothing select nothing or make a rectangle select
		if flag and self.selection != None:
			self.selection = None
		elif flag:
			self.entities_selected = []
			(self.click_x, self.click_y) = mouse.get_pos()
			self.selection_box = Rect(-1, -1, 0, 0)

	def right_click_began(self):
		#set a destination and velocity for all entities
		for entity in self.entities_selected:
			keys = key.get_pressed()
			if not (keys[K_LSHIFT] or entity.path == []):
				entity.path = []
			entity.pathfind(self.camera_mouse())

	def mouse_moved(self):
		#update size of rectangle select
		if (self.click_x, self.click_y) != (None, None):
			width = self.mouse_x() - self.click_x
			height = self.mouse_y() - self.click_y
			self.selection_box.size = (abs(width), abs(height))
			if width < 0 and height < 0:
				self.selection_box.bottomright = (self.click_x, self.click_y)
			elif width < 0 and height > 0:
				self.selection_box.topright = (self.click_x, self.click_y)
			elif width > 0 and height < 0:
				self.selection_box.bottomleft = (self.click_x, self.click_y)
			elif width > 0 and height > 0:
				self.selection_box.topleft = (self.click_x, self.click_y)
			rect = self.selection_box.move(-self.camera_x, -self.camera_y)
			self.entities_selected = [self.entities[i] for i in rect.collidelistall(self.entities)]

	def click_ended(self):
		#select all in rectangle select and the delete rectangle
		if (self.click_x, self.click_y) != (None, None):
			if self.selection_box != None:
				self.selection_box = None
			self.click_x = None
			self.click_y = None

	def draw_world(self):
		start = (-self.camera_x, -self.camera_y)
		area = Rect(start, (screen.get_width(), screen.get_height()))
		self.world.blit(self.world_image, start, area)

	def draw_world_available(self):
		if self.show_world_available:
			for x in range(screen.get_width()/64 + 1):
				for y in range(screen.get_height()/64 + 1):
					if self.world_available[x - self.camera_x/64][y - self.camera_y/64] == False:
						rect = Rect(64*(x - self.camera_x/64), 64*(y - self.camera_y/64), 64, 64)
						draw.rect(self.world, (255, 100, 100), rect)

	def draw_entity_map(self):
		if self.show_world_available:
			for x in range(screen.get_width()/64 + 1):
				for y in range(screen.get_height()/64 + 1):
					if self.entity_map[x - self.camera_x/64][y - self.camera_y/64] != []:
						rect = Rect(64*(x - self.camera_x/64), 64*(y - self.camera_y/64), 64, 64)
						draw.rect(self.world, (255, 100, 100), rect)

	def draw_grid(self):
		if self.show_grid:
			for x in range(screen.get_width()/64 + 1):
				start = (64*x - self.camera_x/64*64, -self.camera_y)
				end = (64*x - self.camera_x/64*64, screen.get_height() - self.camera_y)
				draw.line(self.world, (200, 255, 200), start, end)
			for y in range(screen.get_height()/64 + 1):
				start = (-self.camera_x, 64*y - self.camera_y/64*64)
				end = (screen.get_width() - self.camera_x, 64*y - self.camera_y/64*64)
				draw.line(self.world, (200, 255, 200), start, end)

	def draw_entities(self):
		for entity in self.entities:
			entity.draw_line_to_destination(self.world)
			entity.draw_angles(self.world)
			left = -self.camera_x - entity.rect.width
			right = -self.camera_x + screen.get_width() + entity.rect.width
			top = -self.camera_y -entity.rect.height
			bottom = -self.camera_y + screen.get_height() + entity.rect.height
			if entity != self.selection and left <= entity.x <= right and top <= entity.y <= bottom:
				if entity.rect.collidepoint(self.camera_mouse()):
					entity.draw_health(self.world)
				entity.draw(self.world)

	def draw_entities_health(self):
		for entity in self.entities_selected:
			entity.draw_health(self.world)

	def draw_selection(self):
		if self.selection != None:
			self.selection.draw(self.world)

	def draw_selection_box(self):
		if self.selection_box != None:
			draw.rect(screen, (100, 255, 100), self.selection_box, 5)

	def draw_map(self):
		for entity in self.entities:
			screen.set_at((int(entity.x/64), int(entity.y/64 + screen.get_height() - 256)), entity.color)

	def draw_buttons(self):
		button_background = Rect(screen.get_width() - 256, screen.get_height() - 256, 256, 256)
		draw.rect(screen, (0, 0, 0), button_background)
		for button in self.buttons:
			if button.rect.collidepoint(mouse.get_pos()):
				lighter_color = (button.color[0] + 10, button.color[1] + 10, button.color[2] + 10)
				button.draw(lighter_color)
			else:
				button.draw(button.color)

	def draw(self):
		self.draw_world()
		self.draw_world_available()
		self.draw_grid()
		self.draw_entities()
		self.draw_entities_health()
		self.draw_selection()
		screen.blit(self.world, (self.camera_x, self.camera_y))
		self.draw_selection_box()
		#self.draw_map()
		#self.draw_buttons
		display.update()

	def update_camera(self):
		if self.selection_box == None:
			if self.mouse_x() < 50:
				self.camera_x += 5
			if self.mouse_x() > screen.get_width() - 50:
				self.camera_x -= 5
			if self.mouse_y() < 50:
				self.camera_y += 5
			if self.mouse_y() > screen.get_height() - 50:
				self.camera_y -= 5

	def kill_dead_entities(self):
		i = 0
		while i < len(self.entities):
			if self.entities[i].current_health <= 0:
				if self.entities[i] in self.entities_selected:
					self.entities_selected.remove(self.entities[i])
				del self.entities[i]
				continue
			i += 1

	def update_selection(self):
		if self.selection != None:
			if self.selection.__class__ == Marine:
				self.selection.x, self.selection.y = self.camera_mouse()
			elif self.selection.__class__ == Building:
				self.selection.x, self.selection.y = self.camera_mouse_x()/64*64, self.camera_mouse_y()/64*64

	def update_buttons(self):
		if self.entities_selected != []:
			self.buttons = self.entities_selected[0].buttons
		else:
			self.buttons = []

	def update_entities(self):
		for entity in self.entities:
			entity.update(self.entities)

	def update(self):
		#self.update_camera()
		self.kill_dead_entities()
		self.update_selection()
		self.update_buttons()
		self.update_entities()

if __name__ == '__main__':
	init()
	screen = display.set_mode((3*1366/4, 3*768/4))
	new_game = GameState()