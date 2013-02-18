class SoccerListener:
	def call(self, message):
		words = message.message.split()
		if words[0] == "!fotboll":
			message.done = True
			return "Menade du !fuskboll?"

