from pygame import *
from time import *
from csv import *

class State():

	def __init__(self, screen):
		self.last_right_click = mouse.get_pressed()[0]
		self.last_pos = mouse.get_pos()
		self.last_time = time()
		self.minimized = False
		self.frame = 0
		self.setup()
		self.running = True
		self.handle_update(screen)

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

	def keys(self):
		pass

	def events(self, event):
		pass

	def draw(self):
		pass

	def tick(self, fps = 30):
		interval = 1./fps
		delta = time() - self.last_time
		if delta < interval:
			sleep(interval - delta)
		self.last_time = time()

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
			if evnt.type == KEYDOWN:
				if evnt.key == K_ESCAPE:
					self.stop()
			self.keys()
			self.events(evnt)

	def handle_draw(self, screen):
		self.draw()

	def handle_update(self, screen):
		while self.running:
			self.frame += 1
			a = time()
			self.handle_events()
			b = time()
			self.update()
			c = time()
			self.handle_draw(screen)
			d = time()
			self.tick()	
			with open("data.csv", "a") as csvfile:
				write = writer(csvfile)
				if d - a <.15:
					write.writerow([d - a])
			if d - a > .0333:
				print "frame:", self.frame, "handle events:", b - a, "update:", c - b, "draw:", d - c, "total:", d - a