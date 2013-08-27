
class BasePlugin(object):
	def __init__(self, feed):
		self.feed = feed

	def update(self):
		raise NotImplementedError("Subclassing BasePlugin must implement update method.")
