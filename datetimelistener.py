import datetime
from chatmessage import ChatMessage

class DatetimeListener:
	def call(self, message):
		if message.message == "!week":
			message.done = True
			return self.week()
		elif message.message == "!date" or message == "!time":
			message.done = True
			return self.datetime()

	def week(self):
		return datetime.date.today().isocalendar()[1]

	def datetime(self):
		now = datetime.datetime.now()
		return "%d-%d-%d %d:%d:%d" % (now.year, now.month, now.day, now.hour, now.minute, now.second)