# -*- coding: utf-8 -*-
import Skype4Py

from chatmessage import ChatMessage

# Modules
from tvlistener import TvListener
from youtubelistener import YouTubeListener
from googlelistener import GoogleListener
from wikipedialistener import WikipediaListener
from imdblistener import ImdbListener
from foodlistener import FoodListener
from facebooklistener import FacebookListener
from randomlistener import RandomListener
from spotifylistener import SpotifyListener
from datetimelistener import DatetimeListener
from httplistener import HttpListener
from fredriklistener import FredrikListener
from soccerlistener import SoccerListener

# Register listeners
listeners = [
	TvListener(),
	YouTubeListener(),
	GoogleListener(),
	WikipediaListener(),
	ImdbListener(),
	FoodListener(),
	FacebookListener(),
	RandomListener(),
	DatetimeListener(),
	FredrikListener(),
	SoccerListener(),
	SpotifyListener(),
	HttpListener()
	]

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
		currentMessage = ChatMessage(Message.Body)
		for listener in listeners:
			result = listener.call(currentMessage)
			if currentMessage.done:
				Message.Chat.SendMessage(result)
				break

skype = Skype4Py.Skype()
print 'Connecting to Skype...'
skype.Attach()
print 'Connected to Skype.'
skype.OnAttachmentStatus = OnAttach
skype.OnMessageStatus = OnMessageStatus

Cmd = ''
while not Cmd == 'exit':
	Cmd = raw_input()