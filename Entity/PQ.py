import math

class PQ:

	def __init__(self, (tile, priority)):
		self.queue = [(tile, priority)]

	def insert(self, (tile, priority)):
		L = 0
		R = len(self.queue) - 1
		m = int(math.floor((L + R)/2))
		while L < R:
			m = int(math.floor((L + R)/2))
			if self.queue[m][1] < priority:
				L = m + 1
			if self.queue[m][1] > priority:
				R = m - 1
			elif self.queue[m][1] == priority:
				self.queue.insert(m, (tile, priority))
		self.queue.insert(m, (tile, priority))

	def pop(self):
		return self.queue.pop()[0]
