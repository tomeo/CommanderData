import urllib2
import urllib
from xml.etree import ElementTree
from random import choice
import datetime
from database import Base, Session
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.exc import NoResultFound

class TheTVDBSeries(Base):
    __tablename__ = 'thetvdb_series'

    series_id = Column(String, primary_key=True)
    name = Column(String)
    status = Column(String)
    updated = Column(Integer)

    series_url = '%(mirror)s/api/%(apikey)s/series/%(series_id)s/all/en.xml'
    series_only_url = '%(mirror)s/api/%(apikey)s/series/%(series_id)s/en.xml'
    episode_url = '%(mirror)s/api/%(apikey)s/series/%(series_id)s/default/%(season)s/%(episode)s/en.xml'

    def __init__(self, series_id, name='', updated=0, status=None):
        self.series_id = series_id
        self.name = name
        self.updated = updated
        self.status = status
        self.episodes = []

    def _update_all(self, mirror, apikey, session):

        ser_xml = urllib2.urlopen(self.series_only_url %
                {   'mirror' : mirror,
                    'apikey' : apikey,
                    'series_id' : self.series_id})
        ser_tree = ElementTree.fromstring(ser_xml.read().rstrip('\r'))

        series_tag = ser_tree.find('Series')
        update_time = int(series_tag.find('lastupdated').text)
        if self.updated >= update_time:
            return
        self.updated = update_time
        self.status = series_tag.find('Status').text
        self.name = series_tag.find('SeriesName').text

        all_xml = urllib2.urlopen(self.series_url %
                {   'mirror' : mirror,
                    'apikey' : apikey,
                    'series_id' : self.series_id})
        all_tree = ElementTree.fromstring(all_xml.read().rstrip('\r'))

        for ep_tag in all_tree.iter('Episode'):
            if int(ep_tag.find('SeasonNumber').text) == 0:
                continue
            (year, month, day) = [int(num) for num in
                    ep_tag.find('FirstAired').text.split('-')]
            ep_date = datetime.date(year, month, day)
            ep_updated = int(ep_tag.find('lastupdated').text)
            try:
                ep = session.query(TheTVDBEpisode).\
                        filter(TheTVDBEpisode.episode_id ==\
                            ep_tag.find('id').text).\
                        one()
            except NoResultFound, e:
                ep = TheTVDBEpisode(
                    ep_tag.find('id').text,
                    self.series_id,
                    int(ep_tag.find('SeasonNumber').text),
                    int(ep_tag.find('EpisodeNumber').text),
                    ep_date,
                    ep_updated,
                    ep_tag.find('EpisodeName').text)
                self.episodes.append(ep)
            if ep.updated < ep_updated:
                ep.aired = ep_date
                ep.name = ep_tag.find('EpisodeName').text
        session.add(self)
        session.commit()


    def get_last_episode(self, mirror, apikey, session):
        self._update_all(mirror, apikey, session)
        today = datetime.date.today()
        return session.query(TheTVDBEpisode).\
                join(TheTVDBEpisode.series).\
                filter(TheTVDBEpisode.series == self).\
                filter(TheTVDBEpisode.aired < today).\
                order_by(TheTVDBEpisode.aired.desc()).first()

class TheTVDBEpisode(Base):

    __tablename__ = 'thetvdb_episodes'

    episode_id = Column(Integer, primary_key=True)
    series_id = Column(String, ForeignKey(TheTVDBSeries.series_id))
    season = Column(Integer)
    episode = Column(Integer)
    aired = Column(Date)
    updated = Column(Integer)

    series = relationship(TheTVDBSeries, backref=backref('episodes'))

    def __init__(self, ep_id, series_id, season, episode, aired_date, updated,
            name=""):
        self.episode_id = ep_id
        self.series_id = series_id
        self.season = season
        self.episode = episode
        self.aired = aired_date
        self.name = name

    def __eq__(self, other):
        return self.episode_id == other.episode_id

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
        return '%s, S%02dE%02d, %s' % (self.series.name, self.season,
                self.episode, self.aired)

class TheTVDBAccount(Base):

    __tablename__ = 'thetvdb_accounts'

    name = Column(String, primary_key=True)
    account_id = Column(String)
    series = relationship(TheTVDBSeries, backref=backref('favorite_of'),
            secondary=Table('thetvdb_favorites', Base.metadata,
                Column('account_id', String,
                    ForeignKey('%s.account_id' % __tablename__)),
                Column('series_id', String,
                    ForeignKey(TheTVDBSeries.series_id))
                ))

    favorite_url = '%(mirror)s/api/User_Favorites.php?accountid=%(account_id)s'

    def __init__(self, name, account_id):
        self.name = name
        self.account_id = account_id
        self.series = []

    def _refresh_favorites(self, mirror, session):
        fav_xml = urllib2.urlopen(self.favorite_url %
                {   'mirror' : mirror,
                    'account_id' : self.account_id})
        fav_tree = ElementTree.fromstring(fav_xml.read().rstrip('\r'))
        fav_ids = set([tag.text for tag in fav_tree.iter('Series')])
        for fav_id in fav_ids - set([s.series_id for s in self.series]):
            print("ACCOUNT: found new favorite %s" % fav_id)
            try:
                self.series.append(session.query(TheTVDBSeries).\
                        filter(TheTVDBSeries.series_id == fav_id).one())
            except NoResultFound, e:
                ser = TheTVDBSeries(fav_id)
                self.series.append(ser)
                session.add(ser)
                session.commit()

    def get_last_episodes(self, mirror, apikey, session):
        self._refresh_favorites(mirror, session)
        return [s.get_last_episode(mirror, apikey, session) for s in self.series]

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
        self.session = Session()
        for acc in self.session.query(TheTVDBAccount).all():
            self.accounts[acc.name] = acc

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
            res = 'Already registered the account %s'\
                    'Use !thetvdb deregister to remove your account'\
                    'before trying to register a new' %\
                    self.accounts[msg.fromhandle].account_id
        else:
            self.accounts[msg.fromhandle] =\
                    TheTVDBAccount(str(msg.fromhandle), str(cmd[0]))
            res = 'Registered new account with id %s' % cmd[0]
        return res

    def recent(self, cmd, msg):
        if not msg.fromhandle in self.accounts:
            return "Please register a thetvdb account id first\n!thetvdb register <account_id>"
        last_episodes = self.accounts[msg.fromhandle].get_last_episodes(
                choice(self.mirrors), self.apikey, self.session)
        return '\n'.join([ep.__str__() for ep in last_episodes])

    def save(self):
        self.session.add_all(self.accounts.values())
        self.session.commit()

if __name__ == '__main__':
    from chatmessage import ChatMessage
    msg_reg = ChatMessage('!thetvdb register 676E7F53485976AB', 'oscar')
    msg_rec = ChatMessage('!thetvdb recent', 'oscar')
    tvdb = TheTVDBListener()
    session = Session()
    Base.metadata.create_all(session.connection())
    print(tvdb.call(msg_reg))
    print(tvdb.call(msg_rec))
    print(tvdb.call(msg_rec))
    #acc = TheTVDBAccount('osse_olsson', 'my_id')
    #session.add(acc)
    #session.commit()
    #tvdb.save()
    #print(tvdb.call(msg_rec))
    #ep = TheTVDBEpisode(1, 'test series', 1, 2, date(2012, 1, 2))
    #session.add(ep)
    #session.commit()

