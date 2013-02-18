# -*- coding: utf-8 -*-
class FredrikListener:
	def call(self, message):
		words = message.message.split()
		if words[0] == "!fredrik":
			message.done = True
			return "Fjedjik: " + " ".join(words[1::]).replace('r', 'j').replace(u'at', u'öet')