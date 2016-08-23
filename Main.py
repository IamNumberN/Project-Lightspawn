from Entity import *
from State import *
from Button import *
from Room import *
from Trees import *
from pygame import *
from pygame.locals import *
from sys import *
from math import *
from random import *
from time import *
from csv import *
from pickle import *

def timer(function, *args):
		start = time()
		function(*args)
		end = time()
		print function.__name__, ":", end - start 

def stop_until_click():
	run = True
	while run:
		for evnt in event.get():
			if evnt.type == MOUSEBUTTONDOWN:
				run = False
			if evnt.type == QUIT:
				import sys
				sys.exit()
 
class GameState(State):

	def setup(self):
		self.show_grid = False
		self.move_camera = True
		self.save = False
		self.camera_x = 0
		self.camera_y = 0
		self.side_1_entities = []
		self.side_2_entities = []
		self.world_width = 100
		self.world_height = 100
		self.tile_length = 32
		self.sheet = self.sheet_to_list(image.load("sheet.png"), 8, 6, 32)
		self.world = Surface((self.world_width*self.tile_length, self.world_height*self.tile_length))
		self.tiles = self.generate_tiles(self.world_width, self.world_height)
		self.draw_tiles()
		self.buttons = [Button(self.load, 16, 16), Button(self.toggle_save, 64, 16), Button(self.zoom_in, 112, 16), Button(self.zoom_out, 160, 16)]
		self.entities = self.side_1_entities +  self.side_2_entities
		self.click_x = None
		self.click_y = None
		self.selection_box = None
		self.entities_selected = self.side_1_entities
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
		self.light_level = {}
		self.load_file_name = None
		self.click1 = None

	def sheet_to_list(self, sheet, width, height, size):
		return_lst = [Surface((size, size)) for i in range(width*height)]
		for x in xrange(width):
			for y in xrange(height):
				return_lst[y*width + x].blit(sheet, (0, 0), (x*size, y*size, size, size))
		return_lst.append(image.load("water.png"))
		return return_lst


	def generate_tiles(self, width, height):
		self.tree = BSP_Node(0, 0, width, height)
		self.tree.split()
		tiles = [[Wall(x, y) for y in xrange(height)] for x in xrange(width)]
		self.draw_leaves()
		self.build_rooms(tiles)
		self.build_hallways(tiles)
		return tiles

	def draw_leaves(self):
		leaves = self.tree.get_leaves()
		for leaf in leaves:
			rect = Rect(8*leaf.x, 8*leaf.y, 8*leaf.width, 8*leaf.height)
			draw.rect(screen, (0, 0, 255), rect, 3)
			display.update()
		stop_until_click()

	def build_rooms(self, tiles):
		leaves = self.tree.get_leaves()
		print len(leaves)
		for leaf in leaves:
			# for x in range(randrange(leaf.x + 1, leaf.x + leaf.width/2), randrange(leaf.x + leaf.width/2, leaf.x + leaf.width)):
			# 	for y in range(randrange(leaf.y + 1, leaf.x + leaf.height/2), randrange(leaf.y + leaf.height/2, leaf.y + leaf.height)):
			for x in range(leaf.x + 1, leaf.width - 1):
				for y in range(leaf.y + 1, leaf.height - 1):
					tiles[x][y] = Tile(x, y)

	def build_hallways(self, tiles):
		leaves = self.tree.get_leaves()
		for i in range(len(leaves)/2):
			if leaves[2*i].direction == 1:
				y = leaves[2*i].center_y
				for x in range(leaves[2*i].center_x, leaves[2*i + 1].center_x):
					tiles[x][y] = Tile(x, y)
			else:
				x = leaves[2*i].center_x
				for y in range(leaves[2*i].center_y, leaves[2*i + 1].center_y):
					tiles[x][y] = Tile(x, y)

	#returns the x value of the mouse releative to the screen
	def mouse_x(self):
		return mouse.get_pos()[0]

	#returns the y value of the mouse releative to the screen
	def mouse_y(self):
		return mouse.get_pos()[1] 

	#returns a tuple with the x and y value of the mouse releative to the world
	def camera_mouse(self):
		return self.mouse_x() - self.camera_x, self.mouse_y() - self.camera_y

	#returns the x value of the mouse relative to the world
	def camera_mouse_x(self):
		return self.mouse_x() - self.camera_x

	#returns the x value of the mouse relative to the world
	def camera_mouse_y(self):
		return self.mouse_y() - self.camera_y

	#returns the tile that was clicked on
	def mouse_tile(self):
		x = min(self.world_width - 1, self.camera_mouse_x()/self.tile_length)
		y = min(self.world_height - 1, self.camera_mouse_y()/self.tile_length)
		if x < 0 or y < 0:
			return None
		else:
			return self.tiles[x][y]

	#returns the tile in the center of the screen
	def center_tile(self):
		x = min(self.world_width - 1, (self.camera_mouse_x() + screen.get_width()/2)/self.tile_length)
		y = min(self.world_height - 1, (self.camera_mouse_y() + screen.get_height()/2)/self.tile_length)
		if x < 0 or y < 0:
			return None
		else:
			return self.tiles[x][y]

	#a function that is called when the load button is pressed. Replaces the current tiles with the save
	#one in load_file_name.
	def load(self):
		self.tiles = load(open(self.load_file_name, "r+"))
		self.world_width = len(self.tiles)
		self.world_height = len(self.tiles[0])

	#a function that is called when the toggle save button is pressed. Inverses the save boolean so that
	#the exit function will save the current tiles
	def toggle_save(self):
		self.buttons[1].color = (200, 200, 200) if self.save else (100, 100, 100)
		self.save = not self.save

	def zoom_in(self):
		for entity in self.entities:
			entity.size = int(entity.size*(1 + (8./self.tile_length)))
			entity.x = int(entity.x*(1 + (8./self.tile_length)))
			entity.y = int(entity.y*(1 + (8./self.tile_length)))
		self.camera_x = int((self.camera_x + screen.get_width()/2)/(1 + (8./self.tile_length))) - screen.get_width()/2
		self.camera_y = int((self.camera_y + screen.get_height()/2)/(1 + (8./self.tile_length))) - screen.get_height()/2
		self.tile_length += 8

	def zoom_out(self):
		self.tile_length -= 8
		self.camera_x = int((self.camera_x + screen.get_width()/2)*(1 + (8./self.tile_length))) - screen.get_width()/2
		self.camera_y = int((self.camera_y + screen.get_height()/2)*(1 + (8./self.tile_length))) - screen.get_height()/2
		for entity in self.entities:
			entity.size = int(entity.size/(1 + (8./self.tile_length)))
			entity.x = int(entity.x/(1 + (8./self.tile_length)))
			entity.y = int(entity.y/(1 + (8./self.tile_length)))

	#checks the hitbox of every button and entity to see if they've been clicked on. If nothing was
	#clicked then assume we are selecting entities
	def click_began(self):
		for button in self.buttons:
			if button.rect.collidepoint(mouse.get_pos()):
				button.action()
				return
		keys = key.get_pressed()
		for entity in self.entities:
			if entity.rect.collidepoint(self.camera_mouse()):
				if keys[K_a]:
					if keys[K_LSHIFT]:
						for selected_entity in self.entities_selected:
							selected_entity.command_queue.append((selected_entity.attack, (self.frame, entity)))
					else:
						for selected_entity in self.entities_selected:
							selected_entity.command_queue = [(selected_entity.attack, (self.frame, entity))]
				else:
					self.entities_selected = [entity]
					return
		if keys[K_m] and self.mouse_tile() != None:
			if keys[K_LSHIFT]:
				for selected_entity in self.entities_selected:
					selected_entity.command_queue.append((selected_entity.move, (self.frame, self.mouse_tile())))
			else:
				for selected_entity in self.entities_selected:
					selected_entity.command_queue = [(selected_entity.move, (self.frame, self.mouse_tile()))]
		elif keys[K_p] and self.mouse_tile() != None:
			if keys[K_LSHIFT]:
				for selected_entity in self.entities_selected:
					selected_entity.command_queue.append((selected_entity.patrol, (self.frame, self.mouse_tile())))
			else:
				for selected_entity in self.entities_selected:
					selected_entity.command_queue = [(selected_entity.patrol, (self.frame, self.mouse_tile()))]
			return
		(self.click_x, self.click_y) = mouse.get_pos()
		self.selection_box = Rect(-1, -1, 0, 0)

	#tells all selected entities to pathfind to the clicked tile
	def right_click_began(self):
		keys = key.get_pressed()
		for entity in self.entities:
			if entity.rect.collidepoint(self.camera_mouse()):
				print "why"
				if keys[K_LSHIFT]:
					for selected_entity in self.entities_selected:
						entity.command_queue.append((entity.follow, (self.frame, selected_entity)))
				else:
					for entity in self.entities_selected:
						entity.command_queue = [entity.follow, (self.frame, entity)]
		if self.mouse_tile() != None:
			if keys[K_LSHIFT]:
				for selected_entity in self.entities_selected:
					selected_entity.command_queue.append((selected_entity.move, (self.frame, self.mouse_tile())))
			else:
				for selected_entity in self.entities_selected:
					selected_entity.command_queue = [(selected_entity.move, (self.frame, self.mouse_tile()))]
		# self.line_of_sight_ttt_test()

	def pathfind_test(self):
		for entity in self.entities_selected:
			entity.a_star_with_path_smoothing(self.mouse_tile(), self.tiles, self.tile_length)
			#entity.theta_star(screen, self.mouse_tile(), self.tiles, self.tile_length)

	def line_of_sight_ttt_test(self):
		if self.click1 != None:
			print self.entities[0].draw_line_of_sight_tile_to_tile(screen, self.click1, self.mouse_tile(), self.tiles, self.tile_length)
			self.click1 = None
		else:
			self.click1 = self.mouse_tile()

	def line_of_sight_ptp_test(self):
		if self.click1 != None:
			print self.entities[0].draw_line_of_sight_point_to_point(screen, self.click1, self.camera_mouse(), self.tiles, self.tile_length)
			self.click1 = None
		else:
			self.click1 = self.camera_mouse()


	#if we are trying to select entities then adjust the size to our selection box
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
			self.entities_selected = [self.entities[i] for i in rect.collidelistall(self.side_1_entities)]

	#stop selecting entities
	def click_ended(self):
		if (self.click_x, self.click_y) != (None, None):
			if self.selection_box != None:
				self.selection_box = None
			self.click_x = None
			self.click_y = None

	#define control groups left ctrl and a number sets the group just he number reselects it
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
		if keys[K_s]:
			for entity in self.entities_selected:
				entity.stop()
		for entity in self.entities_selected:
			entity.keys()

	#for every tile on screen that isn't drawn yet draw the tile
	def draw_tiles(self):
		top = max(0, -self.camera_y/self.tile_length - 1)
		bottom = min(self.world_height, (-self.camera_y + screen.get_height())/self.tile_length + 1)
		left = max(0, -self.camera_x/self.tile_length - 1)
		right = min(self.world_width, (-self.camera_x + screen.get_width())/self.tile_length + 1)
		for x in xrange(len(self.tiles)):
			for y in xrange(len(self.tiles[0])):
				self.tiles[x][y].draw(self.world, self.tiles, self.tile_length, self.sheet)

	def draw_world(self):
		screen.blit(self.world, )

	def draw_shadows(self):
		top = max(0, -self.camera_y/self.tile_length - 1)
		bottom = min(self.world_height, (-self.camera_y + screen.get_height())/self.tile_length + 1)
		left = max(0, -self.camera_x/self.tile_length - 1)
		right = min(self.world_width, (-self.camera_x + screen.get_width())/self.tile_length + 1)
		for x in xrange(left, right):
			for y in xrange(top, bottom):
				if self.tiles[x][y].seen:
					self.tiles[x][y].draw(self.world, self.tiles, self.tile_length, self.sheet)

	#draws a line for every 
	def draw_grid(self):
		if self.show_grid:
			length = self.tile_length
			for x in xrange(screen.get_width()/length + 1):
				start = (length*x - self.camera_x/length*length, - self.camera_y)
				end = (length*x - self.camera_x/length*length, screen.get_height() - self.camera_y)
				draw.line(self.world, (200, 255, 200), start, end)
			for y in xrange(screen.get_height()/length + 1):
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
		#self.draw_shadows()
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
		if self.camera_x > 0:
			self.camera_x = 0
		if self.camera_x < -(self.world_width*self.tile_length - screen.get_width()):
			self.camera_x = -(self.world_width*self.tile_length - screen.get_width())
		if self.camera_y > 0:
			self.camera_y = 0
		if self.camera_y < -(self.world_height*self.tile_length - screen.get_height()):
			self.camera_y = -(self.world_height*self.tile_length - screen.get_height())

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
			entity.update(self.side_1_entities, self.side_2_entities, self.frame, self.tiles , self.tile_length)

	def update(self):
		self.update_camera()
		self.kill_dead_entities()
		self.update_entities()

	def stop(self):
		if self.save:
			dump(self.tiles, open(str(time()) + ".txt", "w+"))
		exit()

if __name__ == '__main__':
	init()
	screen = display.set_mode((1366, 768))
	new_game = GameState(screen)