from pygame import *

class Button:

	def __init__(self, action, x, y):
		self.action = action
		self.rect = Rect(x, y, 32, 32)
		self.color = (200, 200, 200)

	def draw(self, screen, color):
		draw.rect(screen, color, self.rect)