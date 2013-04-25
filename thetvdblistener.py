import urllib2
import urllib
from xml.etree import ElementTree
from random import choice
from datetime import date

class TheTVDBEpisode:

    def __init__(self, ep_id, series_name, season, episode, aired_date, name=""):
        self.ep_id = ep_id
        self.series_name = series_name
        self.season = season
        self.episode = episode
        self.aired_date = aired_date
        self.name = name

    def __eq__(self, other):
        return self.ep_id == other.ep_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if self.season == other.season:
            return self.episode > other.episode
        else:
            return self.season > other.season

    def __lt__(self, other):
        if self.season == other.season:
            return self.episode < other.episode
        else:
            return self.season < other.season

    def __str__(self):
        return '%s, S%02dE%02d, %s' % (self.series_name, self.season,
                self.episode, self.aired_date)

class TheTVDBSeries:

    series_url = '%(mirror)s/api/%(apikey)s/series/%(series_id)s/all/en.xml'

    def __init__(self, series_id, name=''):
        self.series_id = series_id
        self.name = name
        self.episodes = []

    def _update_all(self, mirror, apikey, history=1, future=1):
        all_xml = urllib2.urlopen(self.series_url %
                {   'mirror' : mirror,
                    'apikey' : apikey,
                    'series_id' : self.series_id})
        all_tree = ElementTree.fromstring(all_xml.read().rstrip('\r'))
        self.name = all_tree.find('Series').find('SeriesName').text
        last_episode_tag = None
        last_date = None
        future_episode = None
        future_date = None
        today = date.today()
        for ep_tag in all_tree.findall('Episode'):
            date_tag = ep_tag.find('FirstAired')
            if date_tag.text is None:
                print("error: %s" % self.name)
                continue
            (year, month, day) = date_tag.text.split('-')
            ep_date = date(int(year), int(month), int(day))
            if today > ep_date and (last_date is None or ep_date > last_date):
                last_date = ep_date
                last_episode_tag = ep_tag
            elif today <= ep_date and (future_date is None or ep_date < future_date):
                future_date = ep_date
                future_episode_tag = ep_tag
        self.episodes.append(TheTVDBEpisode(
            last_episode_tag.find('id').text,
            all_tree.find('Series').find('SeriesName').text,
            int(last_episode_tag.find('SeasonNumber').text),
            int(last_episode_tag.find('EpisodeNumber').text),
            last_date,
            last_episode_tag.find('EpisodeName').text))

    def get_last_episode(self, mirror, apikey):
        self._update_all(mirror, apikey)
        today = date.today()
        for ep in self.episodes:
            if ep.aired_date < today:
                return ep
        return None

class TheTVDBAccount:

    favorite_url = '%(mirror)s/api/User_Favorites.php?accountid=%(account_id)s'

    def __init__(self, name, account_id):
        self.name = name
        self.account_id = account_id
        self.favorite_ids = set([])
        self.series = []

    def _refresh_favorites(self, mirror):
        fav_xml = urllib2.urlopen(self.favorite_url %
                {   'mirror' : mirror,
                    'account_id' : self.account_id})
        fav_tree = ElementTree.fromstring(fav_xml.read().rstrip('\r'))
        fav_ids = set([tag.text for tag in fav_tree.findall('Series')])
        new_fav_ids = fav_ids - self.favorite_ids
        for fav_id in new_fav_ids:
            self.series.append(TheTVDBSeries(fav_id))

    def get_last_episodes(self, mirror, apikey):
        self._refresh_favorites(mirror)
        eps = []
        for s in self.series:
            eps.append(s.get_last_episode(mirror, apikey))
        return eps


class TheTVDBListener:

    apikey = '559A94F235A8EA20'

    def __init__(self):
        self.commands = {
                'echo': self.echo,
                'register': self.register,
                'recent': self.recent,
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
        self.accounts = {}

    def call(self, msg):
        cmd = msg.message.split()
        if cmd[0] == "!thetvdb" and len(cmd) > 1:
            msg.done = True
            return self.execute_cmd(cmd[1:], msg)
        else:
            return ''

    def execute_cmd(self, cmd, msg):
        if len(cmd) > 0 and cmd[0] in self.commands:
            return self.commands[cmd[0]](cmd[1:], msg)
        else:
            return ''

    def echo(self, cmd, msg):
        return ' '.join(cmd)

    def search(self, cmd, msg):
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

    def register(self, cmd, msg):
        if len(cmd) < 1:
            res = 'Missing account id'
        elif msg.fromhandle in self.accounts:
            if self.accounts[msg.fromhandle].account_id == cmd[0]:
                res = 'Already registered'
            else:
                old_id = self.accounts[msg.fromhandle].account_id
                self.accounts[msg.fromhandle] =\
                        TheTVDBAccount(msg.fromhandle, cmd[0])
                res = 'Changed account id from %s to %s' %\
                        (old_id, self.accounts[msg.fromhandle].account_id)
        else:
            self.accounts[msg.fromhandle] =\
                    TheTVDBAccount(msg.fromhandle, cmd[0])
            res = 'Registered new account with id %s' % cmd[0]
        return res

    def recent(self, cmd, msg):
        if not msg.fromhandle in self.accounts:
            return "Please register a thetvdb account id first\n!thetvdb register <account_id>"
        last_episodes = self.accounts[msg.fromhandle].get_last_episodes(
                choice(self.mirrors), self.apikey)
        return '\n'.join([ep.__str__() for ep in last_episodes])

if __name__ == '__main__':
    from chatmessage import ChatMessage
    msg_reg = ChatMessage('!thetvdb register 676E7F53485976AB', 'oscar')
    msg_rec = ChatMessage('!thetvdb recent', 'oscar')
    tvdb = TheTVDBListener()
    print(tvdb.call(msg_reg))
    print(tvdb.call(msg_rec))

