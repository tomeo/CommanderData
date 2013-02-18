import functions

class ImdbListener:
	def call(self, message):
		words = message.message.split()
		if words[0] == "!i" or words[0] == "!imdb":
			message.done = True
			return self.search("+".join(words[1::]))

	def search(self, term):
		return "http://www.imdb.com/find?q=" + term

	def imdb_info(self, imdb_id):
		api_key = "71e4c2a503c7522113f43f9e04b23fe4"
		imdb_xml = functions.get_markup('http://api.themoviedb.org/2.1/Movie.imdbLookup/en/xml/' + api_key + '/' + imdb_id)
		title = imdb_xml.find('name').text
		release = imdb_xml.find('released').text
		runtime = imdb_xml.find('runtime').text
		rating = imdb_xml.find('rating').text
		plot = imdb_xml.find('overview').text
		return "%s (%s, %s min, %s/10)\n%s." % (title, release, runtime, rating, plot)

	# TODO: Printing trailer url fires title-fetch :(
	# def imdb_url_trailer(self, imdb_id):
	# 	api_key = "71e4c2a503c7522113f43f9e04b23fe4"
	# 	imdb_xml = functions.get_markup('http://api.themoviedb.org/2.1/Movie.imdbLookup/en/xml/' + api_key + '/' + imdb_id)
	# 	tmbd_id = imdb_xml.find('url').text.split('/')[4]

	# 	tmbd_xml = functions.get_markup('http://api.themoviedb.org/2.1/Movie.getInfo/en/xml/' + api_key + '/' + tmbd_id)
	# 	return tmbd_xml.find('trailer').text