from pygame import *
from pygame.locals import *
from sys import *
from time import *
from math import *

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
		display.update()

	def handle_update(self):
		while True:
			self.handle_events()
			self.update()
			self.handle_draw()
			self.tick()

class Entity:

	def __init__(self, x, y, color, current_health):
		self.x = x
		self.y = y
		self.color = color
		self.rect = Rect(x, y, 50, 50)
		self.max_health = 100
		self.current_health = current_health
		self.speed = 3
		self.velocity_x = 0
		self.velocity_y = 0
		self.destination_x = None
		self.destination_y = None
		self.setup()

	def setup(self):
		pass

	def draw(self, screen, camera_pos):
		pass

	def update(self, entities):
		pass

class Marine(Entity):

	def draw(self, screen):
		draw.rect(screen, self.color, self.rect)

	def button4_action(self):
		print "hi"

	def draw_health(self, screen):
		offset = (self.x - (self.max_health - self.rect.width)/2, self.y - 50)
		draw.rect(screen, (0, 0, 0), Rect(offset, (self.max_health, 25)))
		draw.rect(screen, (0, 255, 0), Rect(offset, (self.current_health, 25)))

	def update(self, entities):
		self.rect = Rect(self.x, self.y, 50, 50)
		if (self.destination_x, self.destination_y) != (None, None):
			scale = sqrt((self.x - self.destination_x)**2 + (self.y - self.destination_y)**2)
			if scale < self.speed:
				self.x, self.y = self.destination_x, self.destination_y
				self.destination_x, self.destination_y = None, None
			else:
				new_pos = (self.x + self.velocity_x, self.y + self.velocity_y)
				collisions = Rect(new_pos, (50, 50)).collidelistall(entities)
				if len(collisions) == 1:
					self.x, self.y = new_pos
				else:
					for entity in [entities[i] for i in collisions]:
						entity.current_health -= 1

class Zergling(Entity):

	pass

class Button:

	def __init__(self, action, x, y):
		self.action = action
		self.rect = Rect(x, y, 50, 50)
		self.color = (200, 200, 200)

	def draw(self, color):
		draw.rect(screen, color, self.rect)

class MenuState(State):

	def setup(self):
		self.button1 = Button(self.button1_action, screen.get_width() - 225, screen.get_height() - 225)
		self.button2 = Button(self.button2_action, screen.get_width() - 150, screen.get_height() - 225)
		self.buttons = [self.button1, self.button2]

	def button1_action(self):
		change_state(self, GameState)

	def button2_action(self):
		print "hi"

	def click_began(self):
		for button in self.buttons:
			if button.rect.collidepoint(mouse.get_pos()):
				button.action()

	def draw(self):
		for button in self.buttons:
			if button.rect.collidepoint(mouse.get_pos()):
				lighter_color = (button.color[0] + 10, button.color[1] + 10, button.color[2] + 10)
				draw.rect(screen, lighter_color, button.rect)
			else:
				draw.rect(screen, button.color, button.rect)

class GameState(State):

	def setup(self):
		self.button1 = Button(self.button1_action, screen.get_width() - 225, screen.get_height() - 225)
		self.button2 = Button(self.button2_action, screen.get_width() - 150, screen.get_height() - 225)
		self.button3 = Button(self.button3_action, screen.get_width() - 75, screen.get_height() - 225)
		self.button4 = Button(self.button4_action, screen.get_width() - 225, screen.get_height() - 150)
		self.button5 = Button(self.button5_action, screen.get_width() - 150, screen.get_height() - 150)
		self.button6 = Button(self.button6_action, screen.get_width() - 75, screen.get_height() - 150)
		self.button7 = Button(self.button7_action, screen.get_width() - 225, screen.get_height() - 75)
		self.button8 = Button(self.button8_action, screen.get_width() - 150, screen.get_height() - 75)
		self.button9 = Button(self.button9_action, screen.get_width() - 75, screen.get_height() - 75)
		self.button_row1 = [self.button1, self.button2, self.button3]
		self.button_row2 = [self.button4, self.button5, self.button6]
		self.button_row3 = [self.button7, self.button8, self.button9]
		self.buttons = self.button_row1 + self.button_row2 + self.button_row3
		self.entities = []
		self.selection = None
		self.click_x = None
		self.click_y = None
		self.selection_box = None
		self.entities_selected = []
		self.world = Surface((1000, 1000))
		self.camera_x = 0
		self.camera_y = 0

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

	def button1_action(self):
		new = Marine(0, 0, (220, 220, 220), 100)
		self.entities.append(new)
		if self.selection != None:
			for i in range(len(self.entities)):
				if self.entities[i] == self.selection:
					del self.entities[i]
					break
		self.selection = new

	def button2_action(self):
		new = Marine(0, 0, (220, 220, 220), 5)
		self.entities.append(new)
		if self.selection != None:
			for i in range(len(self.entities)):
				if self.entities[i] == self.selection:
					del self.entities[i]
					break
		self.selection = new

	def button3_action(self):
		change_state(self, GameState)

	def button4_action(self):
		print "hellow"

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

	def click_began(self):
		flag = True
		for button in self.buttons:
			if button.rect.collidepoint(mouse.get_pos()):
				button.action()
				flag = False
		for entity in self.entities:
			if entity.rect.collidepoint(self.camera_mouse()) and entity != self.selection:
				self.entities_selected = [entity]
				flag = False
		if flag and self.selection != None:
			self.selection = None
		elif flag:
			self.entities_selected = []
			(self.click_x, self.click_y) = mouse.get_pos()
			self.selection_box = Rect(-1, -1, 0, 0)

	def right_click_began(self):
		for entity in self.entities_selected:
			entity.destination_x, entity.destination_y = self.camera_mouse()
			scale = sqrt((entity.x - self.camera_mouse_x())**2 + (entity.y - self.camera_mouse_y())**2)
			entity.velocity_x = (self.camera_mouse_x() - entity.x)/scale
			entity.velocity_y = (self.camera_mouse_y() - entity.y)/scale

	def mouse_moved(self):
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
		if (self.click_x, self.click_y) != (None, None):
			if self.selection_box != None:
				self.selection_box = None
			self.click_x = None
			self.click_y = None

	def draw(self):
		self.world.fill((100, 100, 100))
		for entity in self.entities:
			if entity.rect.collidepoint(self.camera_mouse()) and entity != self.selection:
				entity.draw_health(self.world)
			entity.draw(self.world)
		for entity in self.entities_selected:
			entity.draw_health(self.world)
		if self.mouse_x() < 25:
			self.camera_x += 5
		if self.mouse_x() > screen.get_width() - 25:
			self.camera_x -= 5
		if self.mouse_y() < 25:
			self.camera_y += 5
		if self.mouse_y() > screen.get_height() - 25:
			self.camera_y -= 5
		screen.blit(self.world, (self.camera_x, self.camera_y))
		if self.selection_box != None:
			draw.rect(screen, (100, 255, 100), self.selection_box, 5)
		for button in self.buttons:
			if button.rect.collidepoint(mouse.get_pos()):
				lighter_color = (button.color[0] + 10, button.color[1] + 10, button.color[2] + 10)
				button.draw(lighter_color)
			else:
				button.draw(button.color)

	def update(self):
		i = 0
		while i < len(self.entities):
			if self.entities[i].current_health <= 0:
				if self.entities[i] in self.entities_selected:
					self.entities_selected.remove(self.entities[i])
				del self.entities[i]
				continue
			i += 1
		if self.selection != None:
			self.selection.x, self.selection.y = self.camera_mouse()
		if self.entities_selected != []:
			self.button4.action = self.entities_selected[0].button4_action
		else:
			self.button4.action = self.button4_action
		for entity in self.entities:
			entity.update(self.entities)

class CollectionState(State):
	
	def click_began(self):
		change_state(self, MenuState)

	def update(self):
		print "bye"

if __name__ == '__main__':
	init()
	screen = display.set_mode((1200, 900))
	new_game = MenuState()