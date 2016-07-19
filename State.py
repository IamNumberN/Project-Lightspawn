from pygame import *
from time import *

class State():

	def __init__(self, sceen):
		self.last_right_click = mouse.get_pressed()[0]
		self.last_pos = mouse.get_pos()
		self.last_time = time()
		self.minimized = False
		self.count = 0
		self.setup()
		self.handle_update(sceen)

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

	def tick(self, fps = 30):
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

	def handle_draw(self, screen):
		screen.fill((0, 0, 0))
		self.draw()

	def handle_update(self, screen):
		while True:
			a = time()
			self.handle_events()
			b = time()
			self.update()
			c = time()
			self.handle_draw(screen)
			d = time()
			self.tick()	
			# with open("data.csv", "a") as csvfile:
			# 	writer = writer(csvfile)
			# 	writer.writerow([c-b])
			#print "handle events:", b - a, "update:", c - b, "draw:", d - c