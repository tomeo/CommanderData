# export VERSIONER_PYTHON_VERSION=2.6; export VERSIONER_PYTHON_PREFER_32_BIT=yes
import sys
import os
import time
import Skype4Py
import random
import re
from urlparse import urlparse

# La empanada
import json

# Get title of webpage libs
import urllib2
import BeautifulSoup

# Get date
import datetime

# Decode HTML-escapes
import htmlentitydefs

def convert_html_entities(s):
    matches = re.findall("&#\d+;", s)
    if len(matches) > 0:
        hits = set(matches)
        for hit in hits:
            name = hit[2:-1]
            try:
                entnum = int(name)
                s = s.replace(hit, unichr(entnum))
            except ValueError:
                pass

    matches = re.findall("&#[xX][0-9a-fA-F]+;", s)
    if len(matches) > 0:
        hits = set(matches)
        for hit in hits:
            hex = hit[3:-1]
            try:
                entnum = int(hex, 16)
                s = s.replace(hit, unichr(entnum))
            except ValueError:
                pass

    matches = re.findall("&\w+;", s)
    hits = set(matches)
    amp = "&amp;"
    if amp in hits:
        hits.remove(amp)
    for hit in hits:
        name = hit[1:-1]
        if htmlentitydefs.name2codepoint.has_key(name):
            s = s.replace(hit, unichr(htmlentitydefs.name2codepoint[name]))
    s = s.replace(amp, "&")
    return s 

def IsNotNull(value):
    return value is not None and len(value) > 0

def spotify_uri(uri):
	url = 'http://ws.spotify.com/lookup/1/?uri=spotify:' + ':'.join(uri) 
	xml = BeautifulSoup.BeautifulSoup(urllib.urlopen(url))
	name = xml.findAll('name')
	http = http = 'http://open.spotify.com/' + uri[0] + '/' + uri[1]
	
	if uri[0] == 'track':
		artist = 'Artist: ' + name[1].string + '\n'
		title = 'Title: ' + name[0].string + '\n'
		album = 'Album: ' + name[2].string + '\n'
		return artist + title + album + http
	
	if uri[0] == 'album':
		artist = 'Artist: ' + name[1].string + '\n'
		album = 'Album: ' + name[0].string + '\n'
		released = xml.findAll('released')[0].string + '\n'
		return artist + album + released + http

	if uri[0] == 'artist':
		artist = 'Artist: ' + name[0].string + '\n'
		return artist + http

def get_web_title(link):
	soup = BeautifulSoup.BeautifulSoup(urllib2.urlopen(link.geturl()))
	return convert_html_entities(soup.title.string)

def food():
	soup = BeautifulSoup.BeautifulSoup(urllib2.urlopen('http://www.vadihelveteskajaglagatillmiddag.nu/'))
	food = soup.find("p", { "class" : "headline" }).findAll('a')[0]
	return food.string + '\n' + food.get('href')

def tv(show):
	soup = BeautifulSoup.BeautifulSoup(urllib2.urlopen('http://www.tvrage.com/' + show))
	epguide = "http://www.tvrage.com/" + show + "/episode_guide"
	if soup.body.h2 is None:
		return "Can't find show"
	elif soup.body.h2.text.startswith('Next:'):
		return "Next episode: " + re.search('\(([^)]*)\)', soup.body.h2.text).group(0).replace('(','').replace(')','') + '\n' + epguide
	elif soup.body.h2.text.startswith('Prev:'):
		return "No information on next episode. Previous episode: "  + re.search('\(([^)]*)\)', soup.body.h2.text).group(0).replace('(','').replace(')','')  + '\n' + epguide
	else:
		return "No information."


# Fires on attachment status change. Here used to re-attach this script to Skype
# in case attachment is lost.
def OnAttach(status):
	print 'API attachment status: ' + skype.Convert.AttachmentStatusToText(status)
	if status == Skype4Py.apiAttachAvailable:
		skype.Attach()

	if status == Skype4Py.apiAttachSuccess:
		print "Reattached."

# Status: UNKNOWN, SENDING, SENT, RECIEVED, READ
def OnMessageStatus(Message, Status):
	if Status == 'SENT' or Status == 'RECEIVED':
		words = Message.Body.split()

		if words[0] == "!fredrik":
			Message.Chat.SendMessage("Fjedjik: " + " ".join(words[1::]).replace('r', 'j'))

		elif words[0] == "!date" or words[0] == "!time":
			now = datetime.datetime.now()
			Message.Chat.SendMessage("%d-%d-%d %d:%d:%d" % (now.year, now.month, now.day, now.hour, now.minute, now.second));

		elif words[0] == "!g":
			Message.Chat.SendMessage('http://www.google.com/search?q=' + '+'.join(words[1::]))

		elif words[0] == "!y":
			Message.Chat.SendMessage('http://www.youtube.com/results?search_query=' + '+'.join(words[1::]))			

		elif words[0] == "!w":
			Message.Chat.SendMessage('http://en.wikipedia.org/wiki/Special:Search?search=' + '+'.join(words[1::]))			

		elif words[0] == "!imdb":
			Message.Chat.SendMessage('http://www.imdb.com/find?q=' + '+'.join(words[1::]))

		elif words[0] == "!food":
			Message.Chat.SendMessage(food())

		elif words[0] == "!recept":
			Message.Chat.SendMessage('http://www.recept.nu/search?searchtext=' + '+'.join(words[1::]))

		elif words[0] == "!laempanada":
			req = urllib2.Request("http://graph.facebook.com/211608792207500")
			f = urllib2.build_opener().open(req)
			parsed_data = json.load(f)
			Message.Chat.SendMessage(str(parsed_data['likes']) + " people like La Empanada on Facebook.")

		elif words[0] == "!tv":
			Message.Chat.SendMessage(tv("_".join(words[1::])))

		elif words[0] == "!random":
			Message.Chat.SendMessage(random.choice(words[1::]))

		words = Message.Body.split(':')
		if words[0] == "spotify":
			Message.Chat.SendMessage(spotify_uri(words[1::]))

		# Get title from web page
		link = urlparse(Message.Body)
		if IsNotNull(link.geturl()):
			Message.Chat.SendMessage(get_web_title(link))

skype = Skype4Py.Skype()
print 'Connecting to Skype...'
skype.Attach()
print 'Connected to Skype.'
skype.OnAttachmentStatus = OnAttach
skype.OnMessageStatus = OnMessageStatus

Cmd = ''
while not Cmd == 'exit':
	Cmd = raw_input()

