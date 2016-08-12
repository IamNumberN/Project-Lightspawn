from Entity import *
from State import *
from Button import *
from Room import *
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
 
class GameState(State):

	def setup(self):
		self.show_grid = True
		self.move_camera = False
		self.save = False
		self.camera_x = 0
		self.camera_y = 0
		self.world_width = 32
		self.world_height = 32
		self.tile_length = 32
		self.world = Surface((self.world_width*self.tile_length, self.world_height*self.tile_length))
		#self.tiles = [[Tile(x, y) for y in range(self.world_height)] for x in range(self.world_width)]
		self.tiles = self.generate_tiles(self.world_width, self.world_height)
		#self.draw_world()
		self.buttons = [Button(self.load, 16, 16), Button(self.toggle_save, 64, 16), Button(self.zoom_in, 112, 16), Button(self.zoom_out, 160, 16)]
		self.entities = [Entity(self.tiles, 880*i, 406*i, self.tile_length) for i in range(1, 2)]
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
		self.light_level = {}
		self.load_file_name = None
		self.click1 = None

	def generate_tiles(self, width, height):
		tiles = [[Tile(x, y) for y in range(height)] for x in range(width)]
		for x in range(width):
			tiles[x][0] = Wall(x, 0)
			tiles[x][height - 1] = Wall(x, height - 1)
		for y in range(height):
			tiles[0][y] = Wall(0, y)
			tiles[width - 1][y] = Wall(width - 1, y)
		for x in range(5):
			tiles[x + 4][4] = Wall(x + 4, 4)
		tiles[28][13] = Wall(28, 13)
		return tiles


	#returns the x value of the mouse releative to the screen
	def mouse_x(self):
		return mouse.get_pos()[0]

	#returns the yu value of the mouse releative to the screen
	def mouse_y(self):
		return mouse.get_pos()[1] 

	#returns a tuple with the x and y value of the mouse releative to the world
	def camera_mouse(self):
		return self.mouse_x() - self.camera_x, self.mouse_y() - self.camera_y

	#returns the x value of the mouse releative to the world
	def camera_mouse_x(self):
		return self.mouse_x() - self.camera_x

	#returns the x value of the mouse releative to the world
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
				if keys[K_m]:
					if keys[K_LSHIFT]:
						for selected_entity in self.entities_selected:
							selected_entity.command_queue.append(selected_entity.move, (self.frame, entity))
					else:
						for selected_entity in self.entities_selected:
							selected_entity.command_queue = [(selected_entity.move, (self.frame, entity))]
				elif keys[K_a]:
					if keys[K_LSHIFT]:
						for selected_entity in self.entities_selected:
							selected_entity.command_queue.append(selected_entity.attack, (self.frame, entity))
					else:
						for selected_entity in self.entities_selected:
							selected_entity.command_queue = [(selected_entity.attack, (self.frame, entity))]
				elif entity.click_began():
					return
				else:
					self.entities_selected = [entity]
					return
		if keys[K_p] and self.mouse_tile() != None:
			if keys[K_LSHIFT]:
				for selected_entity in self.entities_selected:
					selected_entity.command_queue.append(selected_entity.patrol, (self.frame, self.mouse_tile()))
			else:
				for selected_entity in self.entities_selected:
					selected_entity.command_queue = [(selected_entity.patrol, (self.frame, self.mouse_tile()))]
			return
		(self.click_x, self.click_y) = mouse.get_pos()
		self.selection_box = Rect(-1, -1, 0, 0)

	#tells all selected entities to pathfind to the clicked tile
	def right_click_began(self):
		# keys = key.get_pressed()
		# for entity in self.entities:
		# 	if entity.rect.collidepoint(self.camera_mouse()):
		# 		if keys[K_LSHIFT]:
		# 			for selected_entity in self.entities_selected:
		# 				entity.command_queue.append(entity.follow, (self.frame, selected_entity))
		# 		else:
		# 			for entity in self.entities_selected:
		# 				entity.command_queue = [entity.follow, (self.frame, entity)]
		# if self.mouse_tile() != None:
		# 	if keys[K_LSHIFT]:
		# 		for selected_entity in self.entities_selected:
		# 			start = self.tiles[selected_entity.x/self.tile_length][selected_entity.y/self.tile_length]
		# 			end = self.mouse_tile()
		# 			if end != None and not end.blocked:
		# 				selected_entity.pathfind(start, end, self.world_height, self.world_width, self.tiles, self.tile_length)
		# 			selected_entity.command_queue.append(selected_entity.move, (self.frame, self.mouse_tile(), self.tiles, self.tile_length))
		# 	else:
		# 		for selected_entity in self.entities_selected:
		# 			start = self.tiles[selected_entity.x/self.tile_length][selected_entity.y/self.tile_length]
		# 			end = self.mouse_tile()
		# 			if end != None and not end.blocked:
		# 				selected_entity.pathfind(screen, start, end, self.tiles, self.tile_length)
		# 			selected_entity.command_queue = [(selected_entity.move, (self.frame, self.mouse_tile(), self.tiles, self.tile_length))]
		self.pathfind_test(self):

	def pathfind_test(self):
		pass

	def line_of_sight_ttt_test(self):
		start = self.tiles[self.entities[0].x/self.tile_length][self.entities[0].y/self.tile_length]
		end = self.mouse_tile()
		if self.entities[0].line_of_sight_tile_to_tile(screen, start, end, self.tiles, self.tile_length):
			self.entities[0].path = [self.mouse_tile()]

	def line_of_sight_ptp_test(self):
		if self.click1 != None:
			self.entities[0].line_of_sight_point_to_point(screen, self.click1, self.camera_mouse(), self.tiles, self.tile_length)
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
			self.entities_selected = [self.entities[i] for i in rect.collidelistall(self.entities)]

	#stop selecting entities
	def click_ended(self):
		if (self.click_x, self.click_y) != (None, None):
			if self.selection_box != None:
				self.selection_box = None
			self.click_x = None
			self.click_y = None

	#define control groups left ctrl and a number sets the group just he number reselectes it
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

	#for each entity do a breath first search on valid neighbors to draw field of view. allow peaking past corners
	def draw_FOV(self):
		self.light_level = {}
		for entity in self.entities:
			start = self.tiles[entity.x/self.tile_length][entity.y/self.tile_length]
			top = max(0, -self.camera_y/self.tile_length - 1 - entity.light_radius)
			bottom = min(self.world_height, (-self.camera_y + screen.get_height())/self.tile_length + 1 + entity.light_radius)
			left = max(0, -self.camera_x/self.tile_length - 1 - entity.light_radius)
			right = min(self.world_width, (-self.camera_x + screen.get_width())/self.tile_length + 1 + entity.light_radius)
			start.draw(self.world, start.color, self.tile_length)
			if top < start.y < bottom and left < start.x < right:
				top = max(0, -self.camera_y/self.tile_length - 1)
				bottom = min(self.world_height, (-self.camera_y + screen.get_height())/self.tile_length + 1)
				left = max(0, -self.camera_x/self.tile_length - 1)
				right = min(self.world_width, (-self.camera_x + screen.get_width())/self.tile_length + 1)
				frontier = [start]
				self.light_level[start] = 0
				while frontier != []:
					current = frontier.pop(0)
					for neighbor in current.get_neighbors(self.world_width, self.world_height, self.tiles):
						if self.light_level[current] + 1 < entity.light_radius:
							if not neighbor.seen:
								neighbor.seen = True
							if neighbor not in self.light_level or self.light_level[current] + 1 < self.light_level[neighbor]:
								if neighbor.transparent:
									if start.level >= neighbor.level:
										frontier.append(neighbor)
										self.light_level[neighbor] = self.light_level[current] + 1
										if top < current.y < bottom and left < current.x < right:
											neighbor.draw(self.world, neighbor.color, self.tile_length)

	#for every tile on screen that isn't drawn yet draw the tile
	def draw_world(self):
		top = max(0, -self.camera_y/self.tile_length - 1)
		bottom = min(self.world_height, (-self.camera_y + screen.get_height())/self.tile_length + 1)
		left = max(0, -self.camera_x/self.tile_length - 1)
		right = min(self.world_width, (-self.camera_x + screen.get_width())/self.tile_length + 1)
		for x in range(left, right):
			for y in range(top, bottom):
				# if self.tiles[x][y].seen and self.tiles[x][y] not in self.light_level:
				tile = self.tiles[x][y]
				self.tiles[x][y].draw(self.world, tile.darken(tile.color, .5), self.tile_length)

	#for every tile for every entity cast a ray and draw if it doesn't intersect(super inefficent won't be used)
	def ray_cast_draw_world(self):
		top = max(0, -self.camera_y/self.tile_length - 1)
		bottom = min(self.world_height, (-self.camera_y + screen.get_height())/self.tile_length + 1)
		left = max(0, -self.camera_x/self.tile_length - 1)
		right = min(self.world_width, (-self.camera_x + screen.get_width())/self.tile_length + 1)
		for x in range(left, right):
			for y in range(top, bottom):
				for entity in self.entities:
					start = self.tiles[entity.x/self.tile_length][entity.y/self.tile_length]
					if sqrt((x - start.x)**2 + (y - start.y)**2) > entity.light_radius:
						continue
					entity_top = max(0, -self.camera_y/self.tile_length - 1 - entity.light_radius)
					entity_bottom = min(self.world_height, (-self.camera_y + screen.get_height())/self.tile_length + 1 + entity.light_radius)
					entity_left = max(0, -self.camera_x/self.tile_length - 1 - entity.light_radius)
					entity_right = min(self.world_width, (-self.camera_x + screen.get_width())/self.tile_length + 1 + entity.light_radius)
					if entity_top < start.y < entity_bottom and entity_left < start.x < entity_right:
						if entity.line_of_sight(start, self.tiles[x][y], self.tiles, self.tile_length):
							self.tiles[x][y].draw(self.world, self.tiles[x][y].color, self.tile_length)
							if self.tiles[x][y] not in self.light_level:
								self.light_level[self.tiles[x][y]] = sqrt((x - start.x)**2 + (y - start.y)**2)
							else:
								self.light_level[self.tiles[x][y]] = max(self.light_level[self.tiles[x][y]], sqrt((x - start.x)**2 + (y - start.y)**2))
				if self.tiles[x][y].seen and self.tiles[x][y] not in self.light_level:
					tile = self.tiles[x][y]
					self.tiles[x][y].draw(self.world, tile.darken(tile.color, .5), self.tile_length)

	def calculate_FOV(self):
		self.light_level = {}
		self.a = 0
		for entity in self.entities:
			start = self.tiles[entity.x/self.tile_length][entity.y/self.tile_length]
			entity_top = max(0, -self.camera_y/self.tile_length - 1 - entity.light_radius)
			entity_bottom = min(self.world_height, (-self.camera_y + screen.get_height())/self.tile_length + 1 + entity.light_radius)
			entity_left = max(0, -self.camera_x/self.tile_length - 1 - entity.light_radius)
			entity_right = min(self.world_width, (-self.camera_x + screen.get_width())/self.tile_length + 1 + entity.light_radius)
			#print entity_top, entity_bottom, entity_left, entity_right
			if entity_top < start.y < entity_bottom and entity_left < start.x < entity_right:
				self.recursive_draw_world(0, 1, 0, 0, 1, 1, 0, entity.x/self.tile_length, entity.y/self.tile_length, entity.light_radius)
				self.recursive_draw_world(0, 1, 0, 1, 0, 0, 1, entity.x/self.tile_length, entity.y/self.tile_length, entity.light_radius)
				self.recursive_draw_world(0, 1, 0, 0, -1, 1, 0, entity.x/self.tile_length, entity.y/self.tile_length, entity.light_radius)
				self.recursive_draw_world(0, 1, 0, -1, 0, 0, 1, entity.x/self.tile_length, entity.y/self.tile_length, entity.light_radius)
				self.recursive_draw_world(0, 1, 0, 0, 1, -1, 0, entity.x/self.tile_length, entity.y/self.tile_length, entity.light_radius)
				self.recursive_draw_world(0, 1, 0, 1, 0, 0, -1, entity.x/self.tile_length, entity.y/self.tile_length, entity.light_radius)
				self.recursive_draw_world(0, 1, 0, 0, -1, -1, 0, entity.x/self.tile_length, entity.y/self.tile_length, entity.light_radius)
				self.recursive_draw_world(0, 1, 0, -1, 0, 0, -1, entity.x/self.tile_length, entity.y/self.tile_length, entity.light_radius)
		for tile in self.light_level:
			tile.draw(self.world, tile.darken(tile.color, self.light_level[tile]), self.tile_length)
		#print self.a

	#recursive function that implements FOV using shadowcasting
	def recursive_draw_world(self, row, start, end, xx, xy, yx, yy, startx, starty, radius):
		new_start = 0.
		if start < end:
			return
		blocked = False
		for distance in range(row, radius):
			if not blocked:
				dy = - distance
				for dx in range(-distance, 1):
					self.a += 1
					currentx = startx + dx*xx + dy*xy
					currenty = starty + dx*yx + dy*yy
					left_slope = (dx - .5)/(dy + .5)
					right_slope = (dx + .5)/(dy - .5)
					#if valid tile
					if not (0 <= currentx < self.world_width and 0 <= currenty < self.world_height) or start < right_slope:
						continue
					elif end > left_slope:
						break
					#if within entity's radius light if needed
					if sqrt(dx**2 + dy**2) < radius:
						bright = (1 - sqrt(dx**2 + dy**2)/radius/2)
						if self.tiles[currentx][currenty] not in self.light_level or self.light_level[self.tiles[currentx][currenty]] < bright:
							self.light_level[self.tiles[currentx][currenty]] = bright
							if not self.tiles[currentx][currenty].seen:
								self.tiles[currentx][currenty].seen = True
					# if previous tile was blocking
					if blocked:
						if not self.tiles[currentx][currenty].transparent:
							new_start = right_slope
							continue
						else:
							blocked = False
							start = new_start
					#if we hit a wall withing entity's light radius
					elif not self.tiles[currentx][currenty].transparent and distance < radius:
						blocked = True
						self.recursive_draw_world(distance + 1, start, left_slope, xx, xy, yx, yy, startx, starty, radius)
						new_start = right_slope

	#draws a line for every 
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
		# timer(self.draw_FOV)
		# timer(self.ray_cast_draw_world)
		#self.calculate_FOV()
		self.draw_world()
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
		self.update_camera()
		self.kill_dead_entities()
		self.update_entities()

	def stop(self):
		if self.save:
			dump(self.tiles, open(str(time()) + ".txt", "w+"))
		exit()

if __name__ == '__main__':
	init()
	screen = display.set_mode((1366, 768) )
	new_game = GameState(screen)