from State import *

class Pause(State):

	def click_began(self):
		self.running = False