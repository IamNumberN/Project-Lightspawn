from Entity import *
from Tiles import *
from State import *
from Button import *
from pygame import *
from pygame.locals import *
from sys import *
from math import *
from random import *
from time import *
from csv import *

def change_state(delete, create):
	del delete
	new = create()

def timer(function, *args):
		start = time()
		function(*args)
		end = time()
		print function.__name__, ":", end - start
 
class GameState(State):

	def setup(self):
		self.camera_x = 0
		self.camera_y = 0
		self.world_width = 200
		self.world_height = 200
		self.tile_length = 64
		self.world = Surface((self.world_width*self.tile_length, self.world_height*self.tile_length))
		self.tiles = [[Tile(x, y) for y in range(self.world_height)] for x in range(self.world_width)]
		self.draw_world()
		self.buttons = []
		self.entities = [Entity(self.tiles, 128*i, 128*i) for i in range(1, 3)]
		self.selection = None
		self.click_x = None
		self.click_y = None
		self.selection_box = None
		self.entities_selected = [self.entities[0]]
		self.show_grid = True
		self.show_world_available = True
		self.move_camera = True

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
			start = self.tiles[entity.x/self.tile_length][entity.y/self.tile_length]
			end = self.tiles[self.camera_mouse_x()/self.tile_length][self.camera_mouse_y()/self.tile_length]
			timer(entity.pathfind, start, end, self.world_height, self.world_width, self.tiles)

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
			rect = self.selection_box.move(-self.camera_x, - self.camera_y)
			self.entities_selected = [self.entities[i] for i in rect.collidelistall(self.entities)]

	def click_ended(self):
		#select all in rectangle select and then delete rectangle
		if (self.click_x, self.click_y) != (None, None):
			if self.selection_box != None:
				self.selection_box = None
			self.click_x = None
			self.click_y = None

	def draw_world(self):
		length = self.tile_length
		for x in range(screen.get_width()/length + 2):
			for y in range(screen.get_height()/length + 2):
				self.tiles[x- self.camera_x/length - 1][y- self.camera_y/length - 1].draw(self.world, self.tile_length)
				# rect = Rect(length*(x - self.camera_x/length), length*(y - self.camera_y/length), length, length)
				# draw.rect(self.world, self.tiles[x - self.camera_x/length][y - self.camera_y/length].color, rect)

	def draw_tile_available(self):
		if self.show_world_available:
			length = self.tile_length
			for x in range(screen.get_width()/length + 1):
				for y in range(screen.get_height()/length + 1):
					if self.tiles[x - self.camera_x/length][y - self.camera_y/length].availability == False:
						rect = Rect(length*(x - self.camera_x/length), length*(y - self.camera_y/length), length, length)
						draw.rect(self.world, (255, 100, 100), rect)

	def draw_grid(self):
		if self.show_grid:
			length = self.tile_length
			for x in range(screen.get_width()/length + 1):
				start = (length*x - self.camera_x/length*length, -self.camera_y)
				end = (length*x - self.camera_x/length*length, screen.get_height() - self.camera_y)
				draw.line(self.world, (200, 255, 200), start, end)
			for y in range(screen.get_height()/length + 1):
				start = (-self.camera_x, length*y - self.camera_y/length*length)
				end = (screen.get_width() - self.camera_x, length*y - self.camera_y/length*length)
				draw.line(self.world, (200, 255, 200), start, end)

	def draw_entities(self):
		for entity in self.entities:
			#entity.draw_line_to_destination(self.world)
			entity.draw_angles(self.world)
			entity.draw_path(self.world, self.tile_length)
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
			screen.set_at((entity.x/64, entity.y/64 + screen.get_height() - 256), entity.color)

	def draw_buttons(self):
		button_background = Rect(screen.get_width() - 256, screen.get_height() - 256, 256, 256)
		draw.rect(screen, (0, 0, 0), button_background)
		for button in self.buttons:
			if button.rect.collidepoint(mouse.get_pos()):
				lighter_color = (button.color[0] + 10, button.color[1] + 10, button.color[2] + 10)
				button.draw(lighter_color)
			else:
				button.draw(button.color)

	def draw_neighbors(self):
		tile = self.tiles[self.camera_mouse_x()/self.tile_length][self.camera_mouse_y()/self.tile_length]
		for neighbor in tile.get_neighbors():
			rect = Rect(neighbor.x*self.tile_length, neighbor.y*self.tile_length, self.tile_length, self.tile_length)
			draw.rect(self.world, (0, 0, 0), rect)

	def draw(self):
		self.draw_world()
		self.draw_tile_available()
		#self.draw_neighbors()
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
		if self.move_camera:
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
			entity.update(self.entities, self.tile_length, self.world_width, self.world_height, self.tiles)

	def update(self):
		self.update_camera()
		self.kill_dead_entities()
		self.update_selection()
		self.update_buttons()
		self.update_entities()

if __name__ == '__main__':
	init()
	screen = display.set_mode((1920/2, 1080/2))
	new_game = GameState(screen)