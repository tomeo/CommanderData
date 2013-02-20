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
			if self.hostname(urls[0]) == "open.spotify.com":
				message.done = True
				return self.spotify_url(urls[0])
			elif self.hostname(urls[0]) == "imdb.com":
				message.done = True
				return self.imdb_url(urls[0])
			elif self.hostname(urls[0]) == "i.imgur.com":
				title = self.imgur_url(urls[0])
				if title is not None:
					message.done = True
					return title
			elif self.hostname(urls[0]) == "i.qkme.me":
				title = self.qkme_url(urls[0])
				if title is not None:
					message.done = True
					return title
			title = self.web_title(urls[0]) 
			if title is not None:
				message.done = True
				return title

	def hostname(self, url):
		return urlparse.urlparse(url.replace("www.", "")).hostname

	def spotify_url(self, url):
		spotify_listener = SpotifyListener()
		return spotify_listener.spotify_uri(url.split("/")[3::], True)

	def imdb_url(self, url):
		imdb_listener = ImdbListener()
		return imdb_listener.imdb_info(url.split('/')[4])

	def imgur_url(self, url):
		soup = functions.get_markup(url.replace("i.", "").replace(".jpg", ""))
		if hasattr(soup.title, 'string'):
			return functions.convert_html_entities(soup.title.string)
		return None

	def qkme_url(self, url):
		soup = functions.get_markup(url.replace("i.", "").replace(".jpg", ""))
		if hasattr(soup.title, 'string'):
			return functions.convert_html_entities(soup.title.string)	

	def web_title(self, url):
		soup = functions.get_markup(url)
		if hasattr(soup.title, 'string'):
			return functions.convert_html_entities(soup.title.string)
		return None