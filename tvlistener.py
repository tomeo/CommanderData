import functions
import BeautifulSoup
import re
from datetime import datetime, timedelta

class TvListener:
	def call(self, message):
		words = message.message.split()
		if words[0] == "!today":
			message.done = True
			return self.today()
		elif words[0] == "!tv":
			message.done = True
			return self.tv("_".join(words[1::]))

	def today(self):
		xml = functions.get_markup("http://showrss.karmorra.info/feeds/all.rss")
		shows = []
		for show in xml.findAll('item'):
			show_date = datetime.strptime(show.pubdate.string[:-6], '%a, %d %b %Y %H:%M:%S')
			if show_date.date() >= datetime.now().date() - timedelta(1) and not show.title.string.startswith("HD 720p:"):
				shows.append(show.title.string)
		shows.sort()
		return '\n'.join(shows)

	def tv(self, show):
		soup = functions.get_markup('http://www.tvrage.com/' + show)
		epguide = "http://www.tvrage.com/" + show + "/episode_guide"
		if soup.body.h2 is None:
			return "Can't find show"
		elif soup.body.h2.text.startswith('Next:'):
			return "Next episode: " + re.search('\(([^)]*)\)', soup.body.h2.text).group(0).replace('(','').replace(')','') + '\n' + epguide
		elif soup.body.h2.text.startswith('Prev:'):
			return "No information on next episode. Previous episode: "  + re.search('\(([^)]*)\)', soup.body.h2.text).group(0).replace('(','').replace(')','')  + '\n' + epguide
		else:
			return "No information."