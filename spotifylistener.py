import functions
import BeautifulSoup

class SpotifyListener:
	def call(self, message):
		words = message.message.split(":")
		if words[0] == "spotify":
			message.done = True
			return self.spotify_uri(words[1::])

	def spotify_uri(self, uri, isHttp=False):
		xml = functions.get_markup('http://ws.spotify.com/lookup/1/?uri=spotify:' + ':'.join(uri))
		name = xml.findAll('name')
		if not isHttp:
			http = 'http://open.spotify.com/' + uri[0] + '/' + uri[1]
		else:
			http = ""
		
		if uri[0] == "track":
			artist = 'Artist: ' + name[1].string + '\n'
			title = 'Title: ' + name[0].string + '\n'
			album = 'Album: ' + name[2].string + '\n'
			return artist + title + album + http
		
		if uri[0] == "album":
			artist = 'Artist: ' + name[1].string + '\n'
			album = 'Album: ' + name[0].string + '\n'
			released = xml.findAll('released')[0].string + '\n'
			return artist + album + released + http

		if uri[0] == "artist":
			artist = 'Artist: ' + name[0].string + '\n'
			return artist + http