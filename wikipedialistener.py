class WikipediaListener:
	def call(self, message):
		words = message.message.split()
		if words[0] == "!w" or words[0] == "!wikipedia":
			message.done = True
			return self.search('+'.join(words[1::]))

	def search(self, term):
		return "http://en.wikipedia.org/wiki/Special:Search?search=" + term