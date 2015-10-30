from __future__ import unicode_literals
from sqlalchemy import create_engine, Column, ForeignKey, Integer, String,\
    Boolean, Unicode, Date, DateTime
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base, declared_attr

import config


engine = create_engine(URL(**config.DATABASE))
Session = sessionmaker(bind=engine)
Base = declarative_base()


class BaseMixin(object):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __mapper_args__ = {'always_refresh': True}

    pk = Column(Integer, primary_key=True)


class User(BaseMixin, Base):
    vk_id = Column(String, nullable=False, unique=True)
    data = relationship("UserData", uselist=False, backref='user')


class UserData(BaseMixin, Base):
    user_pk = Column(Integer, ForeignKey('user.pk'))

    name = Column(String)
    skype = Column(String)
    site = Column(String)
    twitter = Column(String)
    instagram = Column(String)
    facebook = Column(String)
    phone = Column(String)
    university = Column(String)
    photo = Column(String)
    birthday = Column(Date)
    hometown = Column(String)
    current_city = Column(String)
    photos = Column(Integer)
    videos = Column(Integer)
    followers = Column(Integer)
    communities = Column(Integer)
    noteworthy_pages = Column(Integer)
    # wallposts = Column(Integer)


class UserActivityLogs(BaseMixin, Base):
    user_pk = Column(Integer, ForeignKey('user.pk'))
    user = relationship("User", backref='activity_logs')

    online = Column(Boolean, default=True)
    status = Column(String)
    last_visit = Column(DateTime(timezone=False))
    last_visit_text = Column(String)
    mobile_version = Column(Boolean, default=False)


Base.metadata.create_all(engine)
