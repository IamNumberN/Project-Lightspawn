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
		pass

	def tick(self, fps = 30):
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
		display.update()

	def handle_update(self):
		while True:
			self.handle_events()
			self.update()
			self.handle_draw()
			self.tick()

class Entity:

	def __init__(self, game, x, y):
		self.game = game
		self.x = x
		self.y = y
		self.color = (0, 0, 0)
		self.rect = Rect(x, y, 50, 50)
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

	def draw_line_to_destination(self, screen):
		if len(self.path) > 1:
			for i in range(len(self.path)):
				if i == 0:
					draw.line(screen, (100, 255, 100), (self.x, self.y), self.path[0])
				else:
					draw.line(screen, (100, 255, 100), self.path[i], self.path[i - 1])

	def draw_health(self, screen):
		offset = (self.x - (self.max_health - self.rect.width)/2, self.y - 50)
		draw.rect(screen, (0, 0, 0), Rect(offset, (self.max_health, 25)))
		draw.rect(screen, (0, 255, 0), Rect(offset, (self.current_health, 25)))

	def setup(self):
		pass

	def draw(self, screen, camera_pos):
		pass

	def update(self, entities):
		pass

class Marine(Entity):

	def setup(self):
		self.color = (255, 100, 100)
		self.max_health = 50
		self.current_health = 50

	def draw(self, screen):
		rect = Rect(self.x + 2, self.y + 2, 46, 46)
		draw.rect(screen, self.color, rect)

	def update(self, entities):
		self.rect = Rect(self.x, self.y, 50, 50)
		if self.path != []:
			scale = sqrt((self.x - self.path[0][0])**2 + (self.y - self.path[0][1])**2)
			self.velocity_x = self.speed*(self.path[0][0] - self.x)/scale
			self.velocity_y = self.speed*(self.path[0][1] - self.y)/scale
			if scale < self.speed:
				self.x, self.y = self.path[0][0], self.path[0][1]
				del self.path[0]
				self.velocity_x, self.velocity_y = 0, 0
		new_pos = (self.x + self.velocity_x, self.y + self.velocity_y)
		collisions = Rect(new_pos, (50, 50)).collidelistall(entities)
		if len(collisions) == 1:
			self.x, self.y = new_pos

class Building(Entity):

	def setup(self):
		self.color = (255, 75, 75)
		self.rect = Rect(self.x, self.y, 150, 150)
		self.max_health = 300
		self.current_health = 300
		self.buttons = [self.game.button1]

	def button1_action(self):
		new = Building(self.game, 0, 0)
		self.game.entities.append(new)
		#if something is alread selected delete it. Then make and select a marine.
		if self.game.selection != None:
			for i in range(len(self.entities)):
				if self.game.entities[i] == self.game.selection:
					del self.game.entities[i]
					break
		self.game.selection = new

	def draw_line_to_destination(self, screen):
		pass

	def draw(self, screen):
		rect = Rect(self.x + 2, self.y + 2, 146, 146)
		draw.rect(screen, self.color, rect)

	def update(self, entities):
		self.rect = Rect(self.x, self.y, 150, 150)

class Button:

	def __init__(self, action, x, y):
		self.action = action
		self.rect = Rect(x, y, 50, 50)
		self.color = (200, 200, 200)

	def draw(self, color):
		draw.rect(screen, color, self.rect)

class GameState(State):

	def setup(self):
		self.button1 = Button(self.button_action, screen.get_width() - 225, screen.get_height() - 225)
		self.button2 = Button(self.button_action, screen.get_width() - 150, screen.get_height() - 225)
		self.button3 = Button(self.button_action, screen.get_width() - 75, screen.get_height() - 225)
		self.button4 = Button(self.button_action, screen.get_width() - 225, screen.get_height() - 150)
		self.button5 = Button(self.button_action, screen.get_width() - 150, screen.get_height() - 150)
		self.button6 = Button(self.button_action, screen.get_width() - 75, screen.get_height() - 150)
		self.button7 = Button(self.button_action, screen.get_width() - 225, screen.get_height() - 75)
		self.button8 = Button(self.button_action, screen.get_width() - 150, screen.get_height() - 75)
		self.button9 = Button(self.button_action, screen.get_width() - 75, screen.get_height() - 75)
		self.button_row1 = [self.button1, self.button2, self.button3]
		self.button_row2 = [self.button4, self.button5, self.button6]
		self.button_row3 = [self.button7, self.button8, self.button9]
		self.buttons = self.button_row1 + self.button_row2 + self.button_row3
		self.entities = [Marine(self, 75*i, 75*i) for i in range(5)] + [Building(self, 500, 500)]
		self.selection = None
		self.click_x = None
		self.click_y = None
		self.selection_box = None
		self.entities_selected = []
		self.world = Surface((1000, 1000))
		self.camera_x = 0
		self.camera_y = 0
		self.show_grid = False

	def button_action(self):
		pass

	def show_grid(self):
		self.show_grid = not self.show_grid
		print self.show_grid

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
			entity.path.append(self.camera_mouse())

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
		self.world.fill((100, 100, 100))
		#show the grid
		if self.show_grid:
			for x in range(self.world.get_width()/50):
				draw.line(self.world, (200, 255, 200), (50*x, 0), (50*x, self.world.get_height()))
			for y in range(self.world.get_height()/50):
				draw.line(self.world, (200, 255, 200), (0, 50*y), (self.world.get_width(), 50*y))
		#draw all entities
		for entity in self.entities:
			entity.draw_line_to_destination(self.world)
			if entity.rect.collidepoint(self.camera_mouse()) and entity != self.selection:
				entity.draw_health(self.world)
			if entity != self.selection:
				entity.draw(self.world)
		#draw the health of all selected entities
		for entity in self.entities_selected:
			entity.draw_health(self.world)
		#move the camera
		if self.selection_box == None:
			if self.mouse_x() < 25:
				self.camera_x += 25
			if self.mouse_x() > screen.get_width() - 25:
				self.camera_x -= 25
			if self.mouse_y() < 25:
				self.camera_y += 25
			if self.mouse_y() > screen.get_height() - 25:
				self.camera_y -= 25
		#draw selection
		if self.selection != None:
			self.selection.draw(self.world)
		screen.blit(self.world, (self.camera_x, self.camera_y))
		#draw selection box
		if self.selection_box != None:
			draw.rect(screen, (100, 255, 100), self.selection_box, 5)
		#draw position for all entities on map
		for entity in self.entities:
			screen.set_at((int(entity.x/50), int(entity.y/50 + screen.get_height() - 250)), entity.color)
		#draw all buttons
		button_background = Rect(screen.get_width() - 250, screen.get_height() - 250, 250, 250)
		draw.rect(screen, (0, 0, 0), button_background)
		for button in self.buttons:
			if button.rect.collidepoint(mouse.get_pos()):
				lighter_color = (button.color[0] + 10, button.color[1] + 10, button.color[2] + 10)
				button.draw(lighter_color)
			else:
				button.draw(button.color)

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
				print self.camera_mouse_x()/50*50, self.camera_mouse_y()/50*50
				self.selection.x, self.selection.y = self.camera_mouse_x()/50*50, self.camera_mouse_y()/50*50
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
			self.buttons = []
		#update all entities
		for entity in self.entities:
			entity.update(self.entities)

if __name__ == '__main__':
	init()
	screen = display.set_mode((1200, 900))
	new_game = GameState()