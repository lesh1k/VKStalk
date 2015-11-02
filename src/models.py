from __future__ import unicode_literals
from sqlalchemy import create_engine, Column, ForeignKey, Integer, String,\
    Boolean, Unicode, Date, DateTime
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from utils import convert_to_snake_case

import urlparse
from datetime import datetime
import pytz
import config


engine = create_engine(URL(**config.DATABASE))
Session = sessionmaker(bind=engine)
Base = declarative_base()


class BaseMixin(object):

    @declared_attr
    def __tablename__(cls):
        return convert_to_snake_case(cls.__name__)

    __mapper_args__ = {'always_refresh': True}

    pk = Column(Integer, primary_key=True)


class User(BaseMixin, Base):
    vk_id = Column(String, nullable=False, unique=True)
    data = relationship("UserData", uselist=False, backref='user')

    @property
    def url(self):
        # generate user specific URLs
        # self.logger.logger.debug('Generating URLs')

        if self.vk_id.isdigit():
            return urlparse.urljoin(config.SOURCE_URL, "id" + self.vk_id)

        return urlparse.urljoin(config.SOURCE_URL, self.vk_id)

    @property
    def last_visit_text(self):
        if self.activity_logs[-1].is_online:
            last_seen_line = 'Online'
        else:
            # TBD check that self.activity_logs[-1].last_visit is actually a datetime
            now = pytz.timezone(config.CLIENT_TZ).localize(datetime.now())
            delta_datetime = now - self.activity_logs[-1].last_visit
            delta_days = (now.date() - self.activity_logs[-1].last_visit.date()).days
            minutes_ago = delta_datetime.seconds / 60

            if minutes_ago < 60:
                last_seen_line = 'last seen {} minutes ago'.format(minutes_ago)
            elif delta_days == 0:
                last_seen_line = self.activity_logs[-1].last_visit.strftime(
                    'last seen today at %H:%M')
            elif delta_days == 1:
                last_seen_line = self.activity_logs[-1].last_visit.strftime(
                    'last seen yesterday at %H:%M')
            else:
                last_seen_line = self.activity_logs[-1].last_visit.strftime(
                    'last seen on %B %d at %H:%M')

        if self.activity_logs[-1].is_mobile:
            last_seen_line += ' [Mobile]'

        return last_seen_line


class UserData(BaseMixin, Base):
    user_pk = Column(Integer, ForeignKey('user.pk'))

    name = Column(String)
    birthday = Column(Date)
    photo = Column(String)
    hometown = Column(String)
    site = Column(String)
    instagram = Column(String)
    facebook = Column(String)
    twitter = Column(String)
    skype = Column(String)
    phone = Column(String)
    university = Column(String)
    studied_at = Column(String)
    wallposts = Column(Integer)
    photos = Column(Integer)
    videos = Column(Integer)
    followers = Column(Integer)
    communities = Column(Integer)
    noteworthy_pages = Column(Integer)
    current_city = Column(String)
    info_1 = Column(String)
    info_2 = Column(String)
    info_3 = Column(String)


class UserActivityLog(BaseMixin, Base):
    user_pk = Column(Integer, ForeignKey('user.pk'))
    user = relationship("User", backref='activity_logs')

    is_online = Column(Boolean, default=True)
    is_mobile = Column(Boolean, default=False)
    status = Column(String)
    updates = Column(String)
    last_visit_lt_an_hour_ago = Column(Boolean, default=False)
    last_visit = Column(DateTime(timezone=True))
    # last_visit_text = Column(String)
    timestamp = Column(DateTime(timezone=True),
                       default=datetime.utcnow)


Base.metadata.create_all(engine)
