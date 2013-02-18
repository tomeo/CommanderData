import functions

class FacebookListener:
	def call(self, message):
		words = message.message.split()
		if words[0] == "!laempanada":
			message.done = True
			return self.laempanada()

	def laempanada(self):
		parsed_data = functions.get_json("http://graph.facebook.com/211608792207500")
		return str(parsed_data['likes']) + " people like La Empanada on Facebook."