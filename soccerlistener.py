class SoccerListener:
	def call(self, message):
		words = message.message.split()
		if words[0] == "!fotboll":
			message.done = True
			return "Menade du !fuskboll?"
		elif words[0] == "!fuskboll":
			message.done = True
			return "http://www.youtube.com/watch?v=VzeKiEtp0m0"

