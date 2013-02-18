class ChatMessage:
	def __init__(self, message):
		self.message = message
		self.done = False

	def test(self):
		return self.message