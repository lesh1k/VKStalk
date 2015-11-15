# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from helpers.utils import parse_int, clear_screen, as_client_tz
from helpers.h_logging import get_logger
from config import settings

import urllib2  # retrieve the page
import urlparse
import sys
import pytz
import socket
import time
import re


class Parser:
    def __init__(self, url):
        self.user = {}
        self.url = url
        self.soup = self.cook_soup()

    def cook_soup(self):
        html = self.fetch_html()
        soup = None
        if html:
            soup = BeautifulSoup(html)
        return soup

    def fetch_html(self):
        html = None
        attempt = 1
        while True:
            try:
                get_logger('file').debug(
                    'Fetching HTML. Attempt: {}'.format(attempt))
                cHandle = urllib2.urlopen(self.url,
                                          timeout=settings.CONNECTION_TIMEOUT)
                html = cHandle.read()
                cHandle.close()
                break
            except socket.timeout, e:
                get_logger('file').error('Connection timed out')
                time.sleep(settings.DATA_FETCH_INTERVAL)
                clear_screen()
            except urllib2.URLError, e:
                get_logger('file').error('URLError reason {0}. Err: {1}'.format(
                    e.reason,
                    e
                ))
                if e.reason and e.reason.errno == 101 \
                   or isinstance(e.reason, socket.gaierror):
                    message = 'Attempt {0}. Network unavailable.'
                    message += ' Retry in {1} seconds...'
                    message = message.format(attempt,
                                             settings.DATA_FETCH_INTERVAL)
                    get_logger('file').error(message)
                    get_logger('console').info(message)
                    time.sleep(settings.DATA_FETCH_INTERVAL)
                    clear_screen()
                else:
                    import ipdb; ipdb.set_trace()
                    raise
            attempt += 1
        if not html:
            get_logger('file').fatal(
                'Could not fetch HTML. Reached MAX_CONNECTION_ATTEMPTS: {}.'
                .format(settings.MAX_CONNECTION_ATTEMPTS)
            )
            exit('Could not fetch HTML')
        return html

    def get_user_data(self):
        if self.is_profile_private():
            exit("Private profile. Access forbidden")

        self.user["name"] = self.get_user_name()
        self.user["status"] = self.get_user_status()
        self.user["is_online"] = self.is_user_online()
        self.user["is_mobile"] = self.is_user_mobile()

        self.user["last_visit"] = self.get_last_seen_datetime()
        self.user["last_visit_lt_an_hour_ago"] = False
        if 'ago' in self.get_user_last_seen_text():
            self.user["last_visit_lt_an_hour_ago"] = True

        user_secondary_data = self.get_user_secondary_data()
        self.user.update(user_secondary_data)

        return self.user

    def is_profile_private(self):
        text_to_find = [
            'You have to log in in order to view this page.',
            'This user deleted their page. Information unavailable.',
            'This page is either deleted or has not been created yet.',
        ]
        for attempt in xrange(settings.MAX_CONNECTION_ATTEMPTS):
            if self.soup(class_="service_msg_null", string=text_to_find):
                clear_screen()
                message = 'User profile private, deleted or does not exist.'
                message += ' Attempt {0} of {1}. Retry in {2} seonds...'
                message = message.format(attempt+1,
                                         settings.MAX_CONNECTION_ATTEMPTS,
                                         settings.DATA_FETCH_INTERVAL)
                get_logger('file').error(message)
                get_logger('console').error(message)
                time.sleep(settings.DATA_FETCH_INTERVAL)
                self.cook_soup()
                profile_private = True
            else:
                get_logger('file').info('Profile PUBLIC. OK!')
                profile_private = False
                break

        return profile_private

    def get_user_name(self):
        username = self.soup.html.head.title.text
        username = username.rstrip(" VK")
        return username

    def get_user_status(self):
        status = self.soup(class_=["status", "pp_status"])
        if status:
            status_text = status[0].text
        else:
            status_text = None
        return status_text

    def is_user_online(self):
        last_seen = self.get_user_last_seen_text()
        if last_seen and last_seen.lower() == "online":
            is_online = True
        else:
            is_online = False
        return is_online

    def is_user_mobile(self):
        is_mobile = False
        if self.soup.find(class_='mlvi') is not None:
            is_mobile = True
        return is_mobile

    def get_last_seen_datetime(self):
        if self.is_user_online():
            return None

        last_seen = self.get_user_last_seen_text()

        if 'today' in last_seen or 'yesterday' in last_seen:
            dt = pytz.timezone(settings.CLIENT_TZ).localize(datetime.now())
            dt = dt.astimezone(pytz.timezone(settings.VK_TZ))
            if 'yesterday' in last_seen:
                dt = dt - timedelta(days=1)
            last_seen_time = datetime.strptime(
                last_seen[last_seen.index("at"):], "at %I:%M %p")
            dt = dt.replace(hour=last_seen_time.hour,
                            minute=last_seen_time.minute)
        elif 'ago' in last_seen:
            dt = pytz.timezone(settings.CLIENT_TZ).localize(datetime.now())
            dt = dt.astimezone(pytz.timezone(settings.VK_TZ))
            last_seen_minutes_ago = parse_int(last_seen)
            try:
                assert isinstance(last_seen_minutes_ago, int)
            except AssertionError:
                err = 'last_seen_minutes_ago must be int. DUMP: {0}={1}; {2}:{3}'
                err = err.format('last_seen', last_seen,
                                 'last_seen_minutes_ago', last_seen_minutes_ago)
                get_logger('file').fatal(err)
                raise
            dt = dt - timedelta(minutes=last_seen_minutes_ago)
        else:
            dt = datetime.strptime(last_seen, "last seen %d %B at %I:%M %p")
            dt = pytz.timezone(settings.VK_TZ).localize(dt)

        dt = dt.replace(second=0, microsecond=0)
        dt = as_client_tz(dt)
        return dt

    def get_user_last_seen_text(self):
        last_seen = self.soup(class_=["lv", "pp_last_activity", "profile_time_lv"])
        if last_seen:
            text = last_seen[0].text
        else:
            text = ""
        return text

    def get_user_secondary_data(self):
        secondary_data = {}
        secondary_data["wallposts"] = self.get_user_number_of_wallposts()
        secondary_data["photo"] = self.get_user_photo_url()
        additional_info = self.get_user_additional_info()
        secondary_data.update(additional_info)
        return secondary_data

    def get_user_number_of_wallposts(self):
        matching_items = self.soup(class_='slim_header',
                                   text=re.compile("\d+ post."))
        if matching_items:
            wallposts_number = parse_int(matching_items[0].text)
            if not wallposts_number:
                wallposts_number = -1
        else:
            wallposts_number = -1
        return wallposts_number

    def get_user_photo_url(self):
        get_logger('file').debug('Getting profile photo URL.')
        photo_url = None
        photo = self.soup.select("#mcont .owner_panel a img")
        if photo:
            photo_url = photo[0].get("src")
        return photo_url

    def get_user_additional_info(self):
        additional_info = {}

        info_from_pinfo_row = self.get_user_info_from_pinfo_row()
        additional_info.update(info_from_pinfo_row)

        info_from_pp_info = self.get_user_info_from_pp_info()
        additional_info.update(info_from_pp_info)

        info_from_profile_menu = self.get_user_info_from_profile_menu()
        additional_info.update(info_from_profile_menu)

        return additional_info

    def get_user_info_from_pinfo_row(self):
        info = {}
        short_profile_info = []
        for item in self.soup(class_='pinfo_row'):
            text = item.text
            if ':' in text:
                short_profile_info.append(text)

        for info_item in short_profile_info:
            item_title, item_value = info_item.split(":")
            item_title = item_title.lower().replace(" ", "_").strip()
            info[item_title] = item_value

        return info

    def get_user_info_from_pp_info(self):
        info = {}
        short_profile_info = []
        for i, item in enumerate(self.soup(class_='pp_info')):
            text = item.text
            tmp = "Info {0}: {1}".format(i+1, text)
            short_profile_info.append(tmp)

        for info_item in short_profile_info:
            item_title, item_value = info_item.split(":")
            item_title = item_title.lower().replace(" ", "_").strip()
            info[item_title] = item_value

        return info

    def get_user_info_from_profile_menu(self):
        data = {}
        extra_data = self.soup.select('.profile_menu .pm_item')
        extra_data_list = []
        for item in extra_data:
            item = item.text.lower()
            if 'show more' not in item:
                extra_data_list.append(item)

        for item in extra_data_list:
            item_parts = item.split()
            value = parse_int(item)
            key = '_'.join([i.lower() for i in item_parts if i != str(value)])
            data[key] = int(value)
        return data
