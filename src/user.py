# -*- coding: utf-8 -*-
import config
import urlparse


class User:
    def __init__(self, user_id):
        # Primary data
        self.id = user_id
        self.name = None
        self.status = None
        self.name = None
        self.status = None
        self.online = None
        self.last_visit = None
        self.mobile_version = None

        # Secondary data
        self.skype = None
        self.site = None
        self.twitter = None
        self.instagram = None
        self.facebook = None
        self.phone = None
        self.university = None
        self.photo = None
        self.birthday = None
        self.hometown = None
        self.current_city = None

    @property
    def url(self):
        # generate user specific URLs
        # self.logger.logger.debug('Generating URLs')

        if self.id.isdigit():
            return urlparse.urljoin(config.SOURCE_URL, "id" + self.id)

        return urlparse.urljoin(config.SOURCE_URL, self.id)
