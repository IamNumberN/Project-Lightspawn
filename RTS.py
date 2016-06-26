from pygame import *
from pygame.locals import *
from sys import *
from time import *
from math import *
from random import *

def change_state(delete, create):
	del delete
	new = create()

class State():

	def __init__(self):
		self.last_right_click = mouse.get_pressed()[0]
		self.last_pos = mouse.get_pos()
		self.last_time = time()
		self.minimized = False
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
		screen.fill((255, 255, 255))
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
			#print "handle events:", b - a, "update:", c - b, "draw:", d - c

class Entity:

	def __init__(self, game, x, y):
		self.game = game
		self.x = x
		self.y = y
		self.color = (0, 0, 0)
		self.rect = Rect(x, y, 64, 64)
		self.max_health = 100
		self.current_health = 100
		self.speed = 10
		self.velocity_x = 0
		self.velocity_y = 0
		self.destination_x = None
		self.destination_y = None
		self.path = []
		self.buttons = []
		self.setup()

	def button1_action(self):
		pass

	def button2_action(self):
		pass

	def button3_action(self):
		pass

	def button4_action(self):
		pass

	def button5_action(self):
		pass

	def button6_action(self):
		pass

	def button7_action(self):
		pass

	def button8_action(self):
		pass

	def button9_action(self):
		pass

	def pathfind(self, destination):
		self.path.append(destination)

	def draw_line_to_destination(self, screen):
		if len(self.path) > 1:
			for i in range(len(self.path)):
				if i == 0:
					draw.line(screen, (100, 255, 100), (self.x, self.y), self.path[0])
				else:
					draw.line(screen, (100, 255, 100), self.path[i], self.path[i - 1])

	def draw_health(self, screen):
		offset = (self.x - (self.max_health - self.rect.width)/2, self.y - 64)
		draw.rect(screen, (0, 0, 0), Rect(offset, (self.max_health, 32)))
		draw.rect(screen, (0, 255, 0), Rect(offset, (self.current_health, 32)))

	def setup(self):
		pass

	def draw(self, screen, camera_pos):
		pass

	def update(self, entities):
		pass

class Marine(Entity):

	def setup(self):
		self.color = (255, 100, 100)
		self.max_health = 64
		self.current_health = 64
		self.speed = 10

	def draw(self, screen):
		rect = Rect(self.x, self.y, 64, 64)
		draw.rect(screen, self.color, rect)

	def update(self, entities):
		self.rect = Rect(self.x, self.y, 64, 64)
		if self.path != []:
			scale = sqrt((self.x - self.path[0][0])**2 + (self.y - self.path[0][1])**2)
			self.velocity_x = self.speed*(self.path[0][0] - self.x)/scale
			self.velocity_y = self.speed*(self.path[0][1] - self.y)/scale
			if scale < self.speed:
				self.x, self.y = self.path[0][0], self.path[0][1]
				del self.path[0]
				self.velocity_x, self.velocity_y = 0, 0
		new_pos = (self.x + self.velocity_x, self.y + self.velocity_y)
		collisions = Rect(new_pos, (64, 64)).collidelistall(entities)
		if len(collisions) == 1:
			self.x, self.y = new_pos

class Building(Entity):

	def setup(self):
		self.color = (255, 75, 75)
		self.rect = Rect(self.x, self.y, 128, 128)
		self.max_health = 300
		self.current_health = 300
		self.buttons = [self.game.button1]
		self.game.world_available[self.x/64][self.y/64] = False
		self.game.world_available[self.x/64 + 1][self.y/64] = False
		self.game.world_available[self.x/64][self.y/64 + 1] = False
		self.game.world_available[self.x/64 + 1][self.y/64 + 1] = False

	def button1_action(self):
		new = Building(self.game, 0, 0)
		self.game.entities.append(new)
		#if something is alread selected delete it. Then make and select a marine.
		if self.game.selection != None:
			for i in range(len(self.game.entities)):
				if self.game.entities[i] == self.game.selection:
					del self.game.entities[i]
					break
		self.game.selection = new

	def draw_line_to_destination(self, screen):
		pass

	def draw(self, screen):
		rect = Rect(self.x, self.y, 128, 128)
		draw.rect(screen, self.color, rect)

	def update(self, entities):
		self.rect = Rect(self.x, self.y, 128, 128)

class Button:

	def __init__(self, action, x, y):
		self.action = action
		self.rect = Rect(x, y, 64, 64)
		self.color = (200, 200, 200)

	def draw(self, color):
		draw.rect(screen, color, self.rect)

class GameState(State):

	def setup(self):
		self.world_width = 128
		self.world_height = 128
		self.tile_length = 64
		self.world = Surface((self.world_width*self.tile_length, self.world_height*self.tile_length))
		self.world_available = [[True for x in range(self.world_width)] for y in range(self.world_height)]
		self.world_image = self.generate_world_image(self.world_width, self.world_height, self.tile_length)
		self.world.blit(self.world_image, (0, 0))
		self.button1 = Button(self.show_grid, screen.get_width() - 240, screen.get_height() - 240)
		self.button2 = Button(self.button_action, screen.get_width() - 160, screen.get_height() - 240)
		self.button3 = Button(self.button_action, screen.get_width() - 80, screen.get_height() - 240)
		self.button4 = Button(self.button_action, screen.get_width() - 240, screen.get_height() - 160)
		self.button5 = Button(self.button_action, screen.get_width() - 160, screen.get_height() - 160)
		self.button6 = Button(self.button_action, screen.get_width() - 80, screen.get_height() - 160)
		self.button7 = Button(self.button_action, screen.get_width() - 240, screen.get_height() - 80)
		self.button8 = Button(self.button_action, screen.get_width() - 260, screen.get_height() - 80)
		self.button9 = Button(self.button_action, screen.get_width() - 80, screen.get_height() - 80)
		self.button_row1 = [self.button1, self.button2, self.button3]
		self.button_row2 = [self.button4, self.button5, self.button6]
		self.button_row3 = [self.button7, self.button8, self.button9]
		self.buttons = self.button_row1 + self.button_row2 + self.button_row3
		self.entities = [Marine(self, 128*i, 128*i) for i in range(1, 4)] + [Building(self, 512, 512)]
		self.selection = None
		self.click_x = None
		self.click_y = None
		self.selection_box = None
		self.entities_selected = []
		self.camera_x = 0
		self.camera_y = 0
		self.show_grid = False

	def button_action(self):
		pass

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
				color = (randrange(255), randrange(255), randrange(255))
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

	def draw(self):
		a = time()
		#draw world
		start = (-self.camera_x, -self.camera_y)
		area = Rect(start, (screen.get_width(), screen.get_height()))
		self.world.blit(self.world_image, start, area)
		#move the camera
		b = time()
		if self.selection_box == None:
			if self.mouse_x() < 25:
				self.camera_x += 25
			if self.mouse_x() > screen.get_width() - 25:
				self.camera_x -= 25
			if self.mouse_y() < 25:
				self.camera_y += 25
			if self.mouse_y() > screen.get_height() - 25:
				self.camera_y -= 25
		#show the grid
		c = time()
		if self.show_grid:
			for x in range(screen.get_width()/64 + 1):
				start = (64*x - self.camera_x/64*64, -self.camera_y)
				end = (64*x - self.camera_x/64*64, screen.get_height() - self.camera_y)
				draw.line(self.world, (200, 255, 200), start, end)
			for y in range(screen.get_height()/64 + 1):
				start = (-self.camera_x, 64*y - self.camera_y/64*64)
				end = (screen.get_width() - self.camera_x, 64*y - self.camera_y/64*64)
				draw.line(self.world, (200, 255, 200), start, end)
		#draw all entities
		d = time()
		for entity in self.entities:
			entity.draw_line_to_destination(self.world)
			if entity.rect.collidepoint(self.camera_mouse()) and entity != self.selection:
				entity.draw_health(self.world)
			if entity != self.selection:
				entity.draw(self.world)
		#draw the health of all selected entities
		e = time()
		for entity in self.entities_selected:
			entity.draw_health(self.world)
		#draw selection
		f = time()
		if self.selection != None:
			self.selection.draw(self.world)
		screen.blit(self.world, (self.camera_x, self.camera_y))
		#draw selection box
		g = time()
		if self.selection_box != None:
			draw.rect(screen, (100, 255, 100), self.selection_box, 5)
		#draw position for all entities on map
		h = time()
		for entity in self.entities:
			screen.set_at((int(entity.x/64), int(entity.y/64 + screen.get_height() - 256)), entity.color)
		#draw all buttons
		i = time()
		button_background = Rect(screen.get_width() - 256, screen.get_height() - 256, 256, 256)
		draw.rect(screen, (0, 0, 0), button_background)
		for button in self.buttons:
			if button.rect.collidepoint(mouse.get_pos()):
				lighter_color = (button.color[0] + 10, button.color[1] + 10, button.color[2] + 10)
				button.draw(lighter_color)
			else:
				button.draw(button.color)
		j = time()
		display.update()
		k = time()
		#print "world:", b - a, "grid:", c - b, "entities:", d - c, "health:", e - d, "camera:", f - e, "selection:", g - f, "selection box:", h - g, "map:", i - h, "buttons:", j - i, "display:", k - j

	def update(self):
		keys = key.get_pressed()
		if keys[K_ESCAPE]:
			exit()
		#kill all dead entities
		i = 0
		while i < len(self.entities):
			if self.entities[i].current_health <= 0:
				if self.entities[i] in self.entities_selected:
					self.entities_selected.remove(self.entities[i])
				del self.entities[i]
				continue
			i += 1
		#make selection follow mouse
		if self.selection != None:
			if self.selection.__class__ == Marine:
				self.selection.x, self.selection.y = self.camera_mouse()
			elif self.selection.__class__ == Building:
				self.selection.x, self.selection.y = self.camera_mouse_x()/64*64, self.camera_mouse_y()/64*64
		#change what buttons do when selecting entities
		if self.entities_selected != []:
			self.button1.action = self.entities_selected[0].button1_action
			self.button2.action = self.entities_selected[0].button2_action
			self.button3.action = self.entities_selected[0].button3_action
			self.button4.action = self.entities_selected[0].button4_action
			self.button5.action = self.entities_selected[0].button5_action
			self.button6.action = self.entities_selected[0].button6_action
			self.button7.action = self.entities_selected[0].button7_action
			self.button8.action = self.entities_selected[0].button8_action
			self.button9.action = self.entities_selected[0].button9_action
			self.buttons = self.entities_selected[0].buttons
		else:
			self.buttons = [self.button1]
		#update all entities
		for entity in self.entities:
			entity.update(self.entities)

if __name__ == '__main__':
	init()
	screen = display.set_mode((1200, 900))
	new_game = GameState()