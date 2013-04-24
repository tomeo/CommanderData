import urllib2
import urllib
from xml.etree import ElementTree
from random import choice

class TheTVDBAccount:

    favorite_url = '%(mirror)s/api/User_Favorites.php?accountid=%(account_id)s'
    series_url = '%(mirror)s/api/%(apikey)s/series/%(series_id)s/en.xml'

    def __init(self, name, account_id):
        self.name = name
        self.account_id = account_id
        self.favorites = set([])

class TheTVDBListener:

    apikey = '559A94F235A8EA20'

    def __init__(self):
        self.commands = {
                'echo': self.echo,
                'search': self.search
                }
        self.mirrors = []
        mirrors_xml = urllib2.urlopen(
                'http://thetvdb.com/api/%(apikey)s/mirrors.xml' %
                {'apikey' : self.apikey})
        mirrors_tree = ElementTree.fromstring(mirrors_xml.read().rstrip('\r'))
        for mirror_tag in mirrors_tree.findall('Mirror'):
            if int(mirror_tag.find('typemask').text) % 2 == 1:
                self.mirrors.append(mirror_tag.find('mirrorpath').text)

    def call(self, msg):
        words = msg.message.split()
        if words[0] == "!thetvdb":
            if len(words) > 1:
                msg.done = True
                return self.execute_cmd(words[1:])
            else:
                return ''

    def execute_cmd(self, cmd):
        if cmd[0] in self.commands:
            return self.commands[cmd[0]](cmd[1:])
        else:
            return ''

    def echo(self, cmd):
        return ' '.join(cmd)

    def search(self, cmd):
        search_xml = urllib2.urlopen(
                'http://thetvdb.com/api/GetSeries.php?seriesname=%s' %\
                        urllib.quote(' '.join(cmd)))
        search_tree = ElementTree.fromstring(search_xml.read().rstrip('\r'))
        series = search_tree.find('Series')
        name = series.find('SeriesName').text
        first = series.find('FirstAired').text
        thetvdb_id = series.find('seriesid').text
        imdb_link = 'http://www.imdb.com/title/%s/' % series.find('IMDB_ID').text
        return '%s, %s\nTheTVDB id: %s\n%s' % ( name, first, thetvdb_id, imdb_link)

