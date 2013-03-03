class SoccerListener:
	def call(self, message):
		words = message.message.split()
		if words[0] == "!fuskboll":
			message.done = True
			return "http://www.youtube.com/watch?v=IHVTYNGS-F4"