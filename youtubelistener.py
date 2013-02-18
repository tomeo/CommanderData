class YouTubeListener:
	def call(self, message):
		words = message.message.split()
		if words[0] == "!y" or words[0] == "!youtube":
			message.done = True
			return self.search("+".join(words[1::]))

	def search(self, term):
		return "http://www.youtube.com/results?search_query=" + term