# -*- coding: utf-8 -*-
import functions
import re

class HttpListener:
	def call(self, message):
		urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.message)
		# TODO: Check if imdb-url
		# TODO: Check if spotify-url
		if len(urls) > 0:
			message.done = True
			return self.web_title(urls[0])

	def web_title(self, url):
		soup = functions.get_markup(url)
		return functions.convert_html_entities(soup.title.string)