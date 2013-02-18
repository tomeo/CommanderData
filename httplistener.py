# -*- coding: utf-8 -*-
import functions
import re
import urlparse
from spotifylistener import SpotifyListener
from imdblistener import ImdbListener

class HttpListener:
	def call(self, message):
		urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.message)
		if len(urls) > 0:
			message.done = True
			if self.hostname(urls[0]) == "open.spotify.com":
				return self.spotify_url(urls[0])
			elif self.hostname(urls[0]) == "www.imdb.com":
				return self.imdb_url(urls[0])
			return self.web_title(urls[0])

	def hostname(self, url):
		return urlparse.urlparse(url).hostname

	def spotify_url(self, url):
		spotify_listener = SpotifyListener()
		return spotify_listener.spotify_uri(url.split("/")[3::], True)

	def imdb_url(self, url):
		imdb_listener = ImdbListener()
		return imdb_listener.imdb_info(url.split('/')[4])

	def web_title(self, url):
		soup = functions.get_markup(url)
		return functions.convert_html_entities(soup.title.string)