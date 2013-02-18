# -*- coding: utf-8 -*-
from chatmessage import ChatMessage
from urlparse import urlparse
import functions
import urllib2
import BeautifulSoup

class HttpListener:
	def call(self, message):
		link = urlparse(message.message)
		# TODO: Check if imdb-url
		# TODO: Check if spotify-url
		if functions.IsNotNull(link.geturl()):
			message.done = True
			return self.web_title(link)

	def web_title(self, link):
		soup = functions.get_markup(link.geturl())
		return functions.convert_html_entities(soup.title.string)