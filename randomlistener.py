import random

class RandomListener:
	def call(self, message):
		words = message.message.split()
		if words[0] == "!random":
			message.done = True
			return self.randomize(words[1::])

	def randomize(self, options):
		return random.choice(options)