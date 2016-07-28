from Entity import *
from Tiles import *
from State import *
from Button import *
from Room00 import *
from pygame import *
from pygame.locals import *
from sys import *
from math import *
from random import *
from time import *
from csv import *
from pickle import *

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
		self.show_grid = False
		self.show_world_available = True
		self.move_camera = False
		self.save = False
		self.camera_x = 0
		self.camera_y = 0
		self.world_width = 100
		self.world_height = 120
		self.tile_length = 64
		self.world = Surface((self.world_width*self.tile_length, self.world_height*self.tile_length))
		self.tiles = [[Tile(x, y) for y in range(self.world_height)] for x in range(self.world_width)]
		self.draw_world()
		self.buttons = [Button(self.load, 16, 16), Button(self.toggle_save, 96, 16)]
		self.entities = [Entity(self.tiles, 128*i, 128*i, self.world_width, self.world_height) for i in range(2, 20)]
		self.click_x = None
		self.click_y = None
		self.selection_box = None
		self.entities_selected = self.entities
		self.frame = 0
		self.load_file_name = "lots of things diagonal.txt"

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

	def mouse_tile(self):
		x = min(self.world_width - 1, self.camera_mouse_x()/self.tile_length)
		y = min(self.world_height - 1, self.camera_mouse_y()/self.tile_length)
		if x < 0 or y < 0:
			return None
		else:
			return self.tiles[x][y]

	def load(self):
		self.tiles = load(open(self.load_file_name, "r+"))
		self.world_width = len(self.tiles)
		self.world_height = len(self.tiles[0])

	def toggle_save(self):
		self.buttons[1].color = (200, 200, 200) if self.save else (100, 100, 100)
		self.save = not self.save

	def click_began(self):
		flag = True
		#detect button click
		for button in self.buttons:
			if button.rect.collidepoint(mouse.get_pos()):
				button.action()
				flag = False
		#detect entity click
		for entity in self.entities:
			if entity.rect.collidepoint(self.camera_mouse()):
				self.entities_selected = [entity]
				flag = False
		if flag:
			#self.entities_selected = []
			self.tiles[self.camera_mouse_x()/64][self.camera_mouse_y()/64].blocked = not self.tiles[self.camera_mouse_x()/64][self.camera_mouse_y()/64].blocked
			(self.click_x, self.click_y) = mouse.get_pos()
			self.selection_box = Rect(-1, -1, 0, 0)

	def right_click_began(self):
		#print "click frame:", self.frame
		#set a destination and velocity for all entities
		for entity in self.entities_selected:
			start = self.tiles[entity.x/self.tile_length][entity.y/self.tile_length]
			end = self.mouse_tile()
			if end != None and not end.blocked:
				entity.pathfind(start, end, self.world_height, self.world_width, self.tiles, self.tile_length)
				#timer(entity.draw_line_of_sight, end, start, self.tiles, self.tile_length, screen)

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
		top = max(0, -self.camera_y/self.tile_length - 1)
		bottom = min(self.world_height, (-self.camera_y + screen.get_height())/self.tile_length + 1)
		left = max(0, -self.camera_x/self.tile_length - 1)
		right = min(self.world_width, (-self.camera_x + screen.get_width())/self.tile_length + 1)
		for x in range(left, right):
			for y in range(top, bottom):
				if self.show_world_available and self.tiles[x][y].blocked == True:
					rect = Rect(self.tile_length*x, self.tile_length*y, self.tile_length, self.tile_length)
					draw.rect(self.world, (255, 100, 100), rect)
				else:
					tile = self.tiles[x][y]
					tile.draw(self.world, tile.color, self.tile_length)

	def draw_grid(self):
		if self.show_grid:
			length = self.tile_length
			for x in range(screen.get_width()/length + 1):
				start = (length*x - self.camera_x/length*length, - self.camera_y)
				end = (length*x - self.camera_x/length*length, screen.get_height() - self.camera_y)
				draw.line(self.world, (200, 255, 200), start, end)
			for y in range(screen.get_height()/length + 1):
				start = (-self.camera_x, length*y - self.camera_y/length*length)
				end = (screen.get_width() - self.camera_x, length*y - self.camera_y/length*length)
				draw.line(self.world, (200, 255, 200), start, end)

	def draw_entities(self):
		for entity in self.entities:
			#entity.draw_line_to_destination(self.world)
			entity.draw_path(self.world, self.tile_length)
			#entity.draw_angles(self.world)
			left = -self.camera_x - entity.size/2
			right = -self.camera_x + screen.get_width() + entity.size/2
			top = -self.camera_y - entity.size/2
			bottom = -self.camera_y + screen.get_height() + entity.size/2
			if left <= entity.x <= right and top <= entity.y <= bottom:
				if entity.rect.collidepoint(self.camera_mouse()):
					entity.draw_health(self.world)
				entity.draw(self.world)

	def draw_selection_box(self):
		if self.selection_box != None:
			draw.rect(screen, (100, 255, 100), self.selection_box, 5)

	def draw_map(self):
		for entity in self.entities:
			screen.set_at((entity.x/64, entity.y/64 + screen.get_height() - 256), entity.color)

	def draw_buttons(self):
		for button in self.buttons:
			if button.rect.collidepoint(mouse.get_pos()):
				lighter_color = (button.color[0] + 10, button.color[1] + 10, button.color[2] + 10)
				button.draw(screen, lighter_color)
			else:
				button.draw(screen, button.color)

	def draw_neighbors(self):
		tile = self.tiles[self.camera_mouse_x()/self.tile_length][self.camera_mouse_y()/self.tile_length]
		for neighbor in tile.get_neighbors():
			rect = Rect(neighbor.x*self.tile_length, neighbor.y*self.tile_length, self.tile_length, self.tile_length)
			draw.rect(self.world, (0, 0, 0), rect)

	def draw(self):
		self.draw_world()
		#self.draw_neighbors()
		self.draw_grid()
		self.draw_entities()
		screen.blit(self.world, (self.camera_x, self.camera_y))
		self.draw_selection_box()
		#self.draw_map()
		self.draw_buttons()
		display.update()

	def update_camera(self):
		if self.move_camera:
			if self.mouse_x() < 50:
				self.camera_x += 10
			if self.mouse_x() > screen.get_width() - 50:
				self.camera_x -= 10
			if self.mouse_y() < 50:
				self.camera_y += 10
			if self.mouse_y() > screen.get_height() - 50:
				self.camera_y -= 10

	def kill_dead_entities(self):
		i = 0
		while i < len(self.entities):
			if self.entities[i].current_health <= 0:
				if self.entities[i] in self.entities_selected:
					self.entities_selected.remove(self.entities[i])
				del self.entities[i]
				continue
			i += 1

	def update_buttons(self):
		if self.entities_selected != []:
			self.buttons = self.entities_selected[0].buttons
		else:
			self.buttons = []

	def update_entities(self):
		for entity in self.entities:
			entity.update(self.entities, self.tile_length, self.tiles)

	def update(self):
		self.frame += 1
		self.update_camera()
		self.kill_dead_entities()
		#self.update_buttons()
		self.update_entities()

	def stop(self):
		if self.save:
			dump(self.tiles, open(str(time()) + ".txt", "w+"))
		exit()

if __name__ == '__main__':
	init()
	screen = display.set_mode((1366, 768), FULLSCREEN)
	new_game = GameState(screen)