import functions
import BeautifulSoup

class FoodListener:
	def call(self, message):
		words = message.message.split();
		if words[0] == "!food":
			message.done = True
			return self.food()
		elif words[0] == "!recept":
			message.done = True
			return self.recept("+".join(words[1::]))

	def food(self):
		soup = functions.get_markup('http://www.vadihelveteskajaglagatillmiddag.nu/')
		food = soup.find("p", { "class" : "headline" }).findAll('a')[0]
		return food.string + '\n' + food.get('href')

	def recept(self, term):
		return "http://www.recept.nu/search?searchtext=" + term