from __future__ import unicode_literals
from sqlalchemy import create_engine, Column, ForeignKey, Integer, String,\
    Boolean, Unicode, Date, DateTime, and_, func
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm.exc import NoResultFound
from helpers.utils import convert_to_snake_case, as_client_tz, delta_minutes
from helpers.h_logging import get_logger
from datetime import datetime, timedelta
from config import settings

import urlparse
import pytz


engine = create_engine(URL(**settings.DATABASE))
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
        if self.vk_id.isdigit():
            user_url = urlparse.urljoin(settings.SOURCE_URL, "id" + self.vk_id)
        else:
            user_url = urlparse.urljoin(settings.SOURCE_URL, self.vk_id)
        return user_url

    @property
    def last_visit_text(self):
        last_log = self.activity_logs[-1]
        if last_log.is_online:
            last_seen_line = 'Online'
        else:
            now = pytz.timezone(settings.CLIENT_TZ).localize(datetime.now())
            last_visit_in_client_tz = as_client_tz(last_log.last_visit)
            minutes_ago = delta_minutes(now, last_visit_in_client_tz)
            delta_days = (now.date() - last_visit_in_client_tz.date()).days

            if minutes_ago < 60:
                last_seen_line = 'last seen {} minutes ago'.format(minutes_ago)
            else:
                if delta_days == 0:
                    strftime_tmpl = 'last seen today at %H:%M'
                elif delta_days == 1:
                    strftime_tmpl = 'last seen yesterday at %H:%M'
                else:
                    strftime_tmpl = 'last seen on %B %d at %H:%M'
                last_seen_line = last_visit_in_client_tz.strftime(strftime_tmpl)

        if last_log.is_mobile:
            last_seen_line += ' [Mobile]'

        return last_seen_line

    @classmethod
    def from_vk_id(cls, vk_id):
        user = cls.get_by_vk_id(vk_id)
        db_session = Session()
        if not user:
            get_logger('file').debug(
                'User with vk_id={} not found. Creating.'.format(vk_id))
            user = cls(vk_id=vk_id)
            db_session.add(user)
            db_session.commit()
        else:
            db_session.add(user)

        if not user.data:
            get_logger('file').debug(
                'UserData absent. Creating and committing')
            user.data = UserData()
            db_session.commit()
        db_session.close()
        return user

    @classmethod
    def get_by_vk_id(cls, vk_id):
        db_session = Session()
        try:
            user = db_session.query(cls).filter_by(vk_id=vk_id).one()
            get_logger('file').debug(
                'User with vk_id={} found and retrieved.'.format(vk_id))
        except NoResultFound, e:
            user = None
        db_session.close()
        return user

    def activity_for(self, start, end):
        db_session = Session()
        query = db_session.query(
            func.count(UserActivityLog.status).label('status_count'),
            UserActivityLog.status
        ).filter(UserActivityLog.user_pk == self.pk)\
            .filter(and_(
                UserActivityLog.timestamp >= start,
                UserActivityLog.timestamp <= end
            ))\
            .group_by(UserActivityLog.status)\
            .order_by('status_count DESC')
        return query.all()

    def get_name(self):
        db_session = Session()
        db_session.add(self)
        user_name = self.data.name
        db_session.close()
        return user_name


class UserData(BaseMixin, Base):
    user_pk = Column(Integer, ForeignKey('user.pk'))

    name = Column(String)
    birthday = Column(String)
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

    @classmethod
    def from_dict(cls, data):
        inst = cls()
        keys = set(data.keys()) & set(cls.__dict__.keys())
        for key in keys:
            setattr(inst, key, data[key])
        return inst

    @staticmethod
    def get_diff(old, new):
        changes = {}
        excluded_attrs = ['pk', 'user_pk', '_sa_instance_state']
        keys = [k for k in old.__dict__.keys()
                if k not in excluded_attrs and "__" not in k]
        for k in keys:
            old_val = getattr(old, k)
            new_val = getattr(new, k)
            if old_val != new_val:
                changes[k] = {'old': old_val, 'new': new_val}
        return changes


class UserActivityLog(BaseMixin, Base):
    user_pk = Column(Integer, ForeignKey('user.pk'))
    user = relationship("User", backref='activity_logs')

    is_online = Column(Boolean, default=True)
    is_mobile = Column(Boolean, default=False)
    status = Column(String)
    updates = Column(String)
    last_visit_lt_an_hour_ago = Column(Boolean, default=False)
    last_visit = Column(DateTime(timezone=True))
    timestamp = Column(DateTime(timezone=True),
                       default=datetime.now)

    @classmethod
    def from_dict(cls, data):
        inst = cls()
        keys = set(data.keys()) & set(cls.__dict__.keys())
        for key in keys:
            setattr(inst, key, data[key])
        return inst

    @staticmethod
    def get_diff(old, new):
        changes = {}
        excluded_attrs = ['pk', 'user_pk', 'user', 'timestamp',
                          '_sa_instance_state']
        keys = [k for k in old.__dict__.keys()
                if k not in excluded_attrs and "__" not in k]
        for k in keys:
            old_val = getattr(old, k)
            new_val = getattr(new, k)
            if old_val != new_val:
                changes[k] = {'old': old_val, 'new': new_val}
        return changes


Base.metadata.create_all(engine)
