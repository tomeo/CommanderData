class GoogleListener:
	def call(self, message):
		words = message.message.split()
		if words[0] == "!g" or words[0] == "!google":
			message.done = True
			return self.search("+".join(words[1::]))

	def search(self, term):
		return "http://www.google.com/search?q=" + term