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
		self.show_world_available = False
		self.move_camera = True
		self.save = False
		self.camera_x = 0
		self.camera_y = 0
		self.world_width = 200
		self.world_height = 200
		self.tile_length = 32
		self.world = Surface((self.world_width*self.tile_length, self.world_height*self.tile_length))
		self.tiles = [[Tile(x, y) for y in range(self.world_height)] for x in range(self.world_width)]
		self.draw_world()
		self.buttons = [Button(self.load, 16, 16), Button(self.toggle_save, 96, 16)]
		self.entities = [Entity(self.tiles, 64*i, 64*i, self.tile_length) for i in range(1, 2)]
		self.click_x = None
		self.click_y = None
		self.selection_box = None
		self.entities_selected = self.entities
		self.entities_selected0 = []
		self.entities_selected1 = []
		self.entities_selected2 = []
		self.entities_selected3 = []
		self.entities_selected4 = []
		self.entities_selected5 = []
		self.entities_selected6 = []
		self.entities_selected7 = []
		self.entities_selected8 = []
		self.entities_selected9 = []
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
		for button in self.buttons:
			if button.rect.collidepoint(mouse.get_pos()):
				button.action()
				flag = False
		for entity in self.entities:
			if entity.rect.collidepoint(self.camera_mouse()):
				self.entities_selected = [entity]
				flag = False
		if flag:
			(self.click_x, self.click_y) = mouse.get_pos()
			self.selection_box = Rect(-1, -1, 0, 0)

	def right_click_began(self):
		for entity in self.entities_selected:
			start = self.tiles[entity.x/self.tile_length][entity.y/self.tile_length]
			end = self.mouse_tile()
			if end != None and not end.blocked:
				entity.pathfind(start, end, self.world_height, self.world_width, self.tiles, self.tile_length)

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
			rect = self.selection_box.move(-self.camera_x, - self.camera_y)
			self.entities_selected = [self.entities[i] for i in rect.collidelistall(self.entities)]

	def click_ended(self):
		if (self.click_x, self.click_y) != (None, None):
			if self.selection_box != None:
				self.selection_box = None
			self.click_x = None
			self.click_y = None

	def keys(self):
		keys = key.get_pressed()
		if keys[K_LCTRL] and keys[K_0]:
			self.entities_selected0 = self.entities_selected
		if not keys[K_LCTRL] and keys[K_1] and self.entities_selected0 != []:
			self.entities_selected = self.entities_selected0
		if keys[K_LCTRL] and keys[K_1]:
			self.entities_selected1 = self.entities_selected
		if not keys[K_LCTRL] and keys[K_1] and self.entities_selected1 != []:
			self.entities_selected = self.entities_selected1
		if keys[K_LCTRL] and keys[K_2]:
			self.entities_selected2 = self.entities_selected
		if not keys[K_LCTRL] and keys[K_2] and self.entities_selected2 != []:
			self.entities_selected = self.entities_selected2
		if keys[K_LCTRL] and keys[K_3]:
			self.entities_selected3 = self.entities_selected
		if not keys[K_LCTRL] and keys[K_3] and self.entities_selected3 != []:
			self.entities_selected = self.entities_selected3
		if keys[K_LCTRL] and keys[K_4]:
			self.entities_selected4 = self.entities_selected
		if not keys[K_LCTRL] and keys[K_4] and self.entities_selected4 != []:
			self.entities_selected = self.entities_selected4
		if keys[K_LCTRL] and keys[K_5]:
			self.entities_selected5 = self.entities_selected
		if not keys[K_LCTRL] and keys[K_5] and self.entities_selected5 != []:
			self.entities_selected = self.entities_selected5
		if keys[K_LCTRL] and keys[K_6]:
			self.entities_selected6 = self.entities_selected
		if not keys[K_LCTRL] and keys[K_6] and self.entities_selected6 != []:
			self.entities_selected = self.entities_selected6
		if keys[K_LCTRL] and keys[K_7]:
			self.entities_selected7 = self.entities_selected
		if not keys[K_LCTRL] and keys[K_7] and self.entities_selected7 != []:
			self.entities_selected = self.entities_selected7
		if keys[K_LCTRL] and keys[K_8]:
			self.entities_selected8 = self.entities_selected
		if not keys[K_LCTRL] and keys[K_8] and self.entities_selected8 != []:
			self.entities_selected = self.entities_selected8
		if keys[K_LCTRL] and keys[K_9]:
			self.entities_selected9 = self.entities_selected
		if not keys[K_LCTRL] and keys[K_9] and self.entities_selected9 != []:
			self.entities_selected = self.entities_selected9

	def on_screen(self, tile):
		top = max(0, -self.camera_y/self.tile_length - 1)
		bottom = min(self.world_height, (-self.camera_y + screen.get_height())/self.tile_length + 1)
		left = max(0, -self.camera_x/self.tile_length - 1)
		right = min(self.world_width, (-self.camera_x + screen.get_width())/self.tile_length + 1)
		return left < tile.x < right and top < tile.y < bottom

	def light_level(self, start, end):
		return sqrt((end.x - start.x)**2 + (end.y - start.y)**2)

	def draw_FOV(self): 
		light_level = {}
		for entity in self.entities:
			start = self.tiles[entity.x/self.tile_length][entity.y/self.tile_length]
			frontier = []
			frontier.append(start)
			light_level[start] = entity.light_radius
			cost_so_far = {}
			cost_so_far[start] = 0
			while frontier != []:
				current = frontier[0]
				frontier.pop(0)
				for neighbor in current.get_neighbors(self.world_width, self.world_height, self.tiles):
					neighbor_light_level = entity.light_radius - self.light_level(start, neighbor)
					on_screen = self.on_screen(neighbor)
					compare_light_level = neighbor not in light_level or light_level[neighbor] < neighbor_light_level
					tile_is_see_through = neighbor.transparent
					within_light_radius = cost_so_far[current] + 1 < entity.light_radius
					not_going_up_a_level = neighbor.level <= start.level
					if on_screen and compare_light_level and tile_is_see_through and within_light_radius and not_going_up_a_level:
						cost_so_far[neighbor] = cost_so_far[current] + sqrt((neighbor.x - start.x)**2 + (neighbor.y - start.y)**2)/entity.light_radius
						neighbor.draw(self.world, neighbor.darken(neighbor.color, .9 + .1*neighbor_light_level), self.tile_length)
						light_level[neighbor] = neighbor_light_level
						frontier.append(neighbor)
					if not neighbor.seen:
						neighbor.seen = True

	def draw_world(self):
		top = max(0, -self.camera_y/self.tile_length - 1)
		bottom = min(self.world_height, (-self.camera_y + screen.get_height())/self.tile_length + 1)
		left = max(0, -self.camera_x/self.tile_length - 1)
		right = min(self.world_width, (-self.camera_x + screen.get_width())/self.tile_length + 1)
		for x in range(left, right):
			for y in range(top, bottom):
				if self.show_world_available and self.tiles[x][y].blocked:# and self.tiles[x][y].seen:
					rect = Rect(self.tile_length*x, self.tile_length*y, self.tile_length, self.tile_length)
					draw.rect(self.world, darken((255, 100, 100), .9), rect)
				elif self.tiles[x][y].seen:
					tile = self.tiles[x][y]
					tile.draw(self.world, tile.darken(tile.color, .7), self.tile_length)

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

	def draw_enities_selected(self):
		for entity in self.entities_selected:
			left = -self.camera_x - entity.size/2
			right = -self.camera_x + screen.get_width() + entity.size/2
			top = -self.camera_y - entity.size/2
			bottom = -self.camera_y + screen.get_height() + entity.size/2
			if left <= entity.x <= right and top <= entity.y <= bottom:
				entity.draw_selected(self.world)

	def draw_entities(self):
		for entity in self.entities:
			left = -self.camera_x - entity.size/2
			right = -self.camera_x + screen.get_width() + entity.size/2
			top = -self.camera_y - entity.size/2
			bottom = -self.camera_y + screen.get_height() + entity.size/2
			if left <= entity.x <= right and top <= entity.y <= bottom:
				entity.draw(self.world)

	def draw_selection_box(self):
		if self.selection_box != None:
			draw.rect(screen, (100, 255, 100), self.selection_box, 5)

	def draw_buttons(self):
		for button in self.buttons:
			if button.rect.collidepoint(mouse.get_pos()):
				lighter_color = (button.color[0] + 10, button.color[1] + 10, button.color[2] + 10)
				button.draw(screen, lighter_color)
			else:
				button.draw(screen, button.color)

	def draw(self):
		self.draw_world()
		self.draw_FOV()
		self.draw_grid()
		self.draw_enities_selected()
		self.draw_entities()
		screen.blit(self.world, (self.camera_x, self.camera_y))
		self.draw_selection_box()
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

	def update_entities(self):
		for entity in self.entities:
			entity.update(self.entities, self.tile_length, self.tiles, self.frame)

	def update(self):
		self.frame += 1
		self.update_camera()
		self.kill_dead_entities()
		self.update_entities()

	def stop(self):
		if self.save:
			dump(self.tiles, open(str(time()) + ".txt", "w+"))
		exit()

if __name__ == '__main__':
	init()
	screen = display.set_mode((1366, 768), FULLSCREEN)
	new_game = GameState(screen)