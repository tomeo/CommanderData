class ImdbListener:
	def call(self, message):
		words = message.message.split()
		if words[0] == "!i" or words[0] == "!imdb":
			message.done = True
			return self.search("+".join(words[1::]))

	def search(self, term):
		return "http://www.imdb.com/find?q=" + term

	def imdb_info(self, imdb_id):
		parsed_data = functions.get_json("http://imdbapi.org/?id=" + imdb_id + "&type=json&plot=simple&episode=0&lang=en-US&aka=simple&release=simple&business=0&tech=0")
		title_year = "%(title)s (%(year)s)" % parsed_data
		runtime = 'Runtime: ' + ' ,'.join(parsed_data['runtime'])
		directors = 'Directed by ' + ', '.join(parsed_data['directors'])
		rating = "Rating: %(rating)s/10 (%(rating_count)s votes)" % parsed_data
		plot = parsed_data['plot_simple']
		genres = 'Genres: ' + ', '.join(parsed_data['genres'])
		actors = 'Actors: ' + ', '.join(parsed_data['actors'])
		poster = 'Poster: ' + parsed_data['poster']
		trailer = 'Trailer: ' + imdb_url_trailer(imdb_id)
		return "%s.\n%s.\n%s.\n%s.\n%s.\n%s.\n%s\n%s\n\n%s" % (title_year, runtime, rating, genres, directors, actors, poster, trailer, plot)

	def imdb_url_trailer(self, imdb_id):
		api_key = "71e4c2a503c7522113f43f9e04b23fe4"
		imdb_xml = functions.get_markup('http://api.themoviedb.org/2.1/Movie.imdbLookup/en/xml/' + api_key + '/' + imdb_id)
		tmbd_id = imdb_xml.find('url').text.split('/')[4]

		tmbd_xml = functions.get_markup('http://api.themoviedb.org/2.1/Movie.getInfo/en/xml/' + api_key + '/' + tmbd_id)
		return tmbd_xml.find('trailer').text