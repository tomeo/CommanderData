class ChatMessage:
	def __init__(self, message, fromhandle):
		self.message = message
		self.done = False
		self.fromhandle = fromhandle 

	def test(self):
		return self.message