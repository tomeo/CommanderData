from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class SessionFactory(object):

    _session = None

    def __init__(self):
        pass

    def session(self):
        if SessionFactory._session is None:
            engine = create_engine('sqlite:///commanderdata.db', echo=True)
            Session = sessionmaker(bind=engine)
            SessionFactory._session = Session()
        return SessionFactory._session
