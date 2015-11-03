# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from utils import get_all_digits_from_str
from config import settings

import urllib2  # retrieve the page
import urlparse
import sys
import pytz


class Parser:
    def __init__(self, url):
        self.user = {}
        self.url = url
        self.cook_soup()

    def cook_soup(self):
        html = self.fetch_html()
        if html:
            self.soup = BeautifulSoup(html)
        else:
            return False

        return True

    def fetch_html(self):
        try:
            cHandle = urllib2.urlopen(self.url, timeout=20)
            html = cHandle.read()
            cHandle.close()
        except Exception as e:
            print "Error in '{}'".format(sys._getframe().f_code.co_name)
            import ipdb; ipdb.set_trace()

        return html

    def get_user_data(self):
        if self.is_profile_private():
            exit("Private profile. Access forbidden")

        # :Data fetching
        # :Name
        self.user["name"] = self.get_user_name()

        # :Status
        self.user["status"] = self.get_user_status()

        # :Mobile version or not
        self.user["is_mobile"] = self.is_user_mobile()

        # :Online OR not [last seen time]
        self.user["is_online"] = self.is_user_online()
        self.user["last_visit"] = self.get_last_seen_datetime()
        self.user["last_visit_lt_an_hour_ago"] = False
        if 'ago' in self.get_user_last_seen_text():
            self.user["last_visit_lt_an_hour_ago"] = True
            # self.user["last_visit"] = None

        # :Secondary data fectching
        user_secondary_data = self.get_user_secondary_data()
        self.user.update(user_secondary_data)

        return self.user

    def is_profile_private(self):
        max_attempts = settings.MAX_CONNECTION_ATTEMPTS
        for attempt in xrange(1, max_attempts + 1):
            if ((self.soup.find('div', {'class': 'service_msg_null'}))
                    or ('This user deleted their page. Information unavailable.' in self.soup.text)
                    or ('This page is either deleted or has not been created yet.' in self.soup.text)):
                self.cook_soup()
                profile_private = True
            else:
                # self.vk_logger.logger.debug('Profile PUBLIC. OK!')
                profile_private = False
                break

        return profile_private

    def get_user_name(self):
        try:
            username = self.soup.html.head.title.text
            username = username.rstrip(" VK")
        except Exception as e:
            print "Error in '{}'".format(sys._getframe().f_code.co_name)
        return username

    def get_user_status(self):
        # self.vk_logger.logger.debug('Obtaining user status')
        status = self.soup.find('div', {"class": "status"})
        if status:
            status_text = status.text
        else:
            status = self.soup.find('div', {'class': 'pp_status'})
            if status:
                status_text = status.text
            else:
                status_text = None
        return status_text

    def is_user_mobile(self):
        is_mobile = False
        try:
            if self.soup.find(class_='mlvi') is not None:
                is_mobile = True
            return is_mobile
        except Exception as e:
            print "Error in '{}'".format(sys._getframe().f_code.co_name)

    def is_user_online(self):
        # Assuming that the user is online, unless last_seen text is found
        is_online = True
        try:
            last_seen = self.get_user_last_seen_text()
            if last_seen and last_seen != '':
                is_online = False
                if last_seen.lower() == 'online':
                    is_online = True

        except Exception as e:
            print "Error in '{}'".format(sys._getframe().f_code.co_name)

        return is_online

    def get_user_last_seen_text(self):
        last_seen = self.soup.find('div', {'class': 'lv'})
        if last_seen:
            last_seen = last_seen.text
        else:
            last_seen = self.soup.find(
                'div', {'class': 'pp_last_activity'})
            if last_seen:
                last_seen = last_seen.text
            else:
                last_seen = self.soup.find('b', {'id': 'profile_time_lv'})
                if last_seen:
                    last_seen = last_seen.text
                else:
                    last_seen = ""
        return last_seen

    def get_last_seen_datetime(self):
        try:
            last_seen = self.get_user_last_seen_text()

            if not last_seen or last_seen.lower() == "online":
                return None

            if 'today' in last_seen or 'yesterday' in last_seen:
                if 'today' in last_seen:
                    dt = datetime.today()
                else:
                    dt = datetime.fromordinal(datetime.today().toordinal()-1)
                last_seen_time = datetime.strptime(
                    last_seen[last_seen.index("at"):],
                    "at %I:%M %p")
                dt = dt.replace(hour=last_seen_time.hour,
                                minute=last_seen_time.minute)
            elif 'ago' in last_seen:
                dt = datetime.now()
                last_seen_minutes_ago = int(get_all_digits_from_str(last_seen))
                dt = dt - timedelta(minutes=last_seen_minutes_ago)
            else:
                dt = datetime.strptime(last_seen, "last seen %d %B at %I:%M %p")

            year = datetime.now().year
            dt = dt.replace(year=year, second=0, microsecond=0)
            if 'ago' in last_seen:
                dt = pytz.timezone(settings.CLIENT_TZ).localize(dt)
            else:
                dt = pytz.timezone(settings.VK_TZ).localize(dt)
            dt = dt.astimezone(pytz.timezone(settings.CLIENT_TZ))
        except Exception as e:
            print "Error in '{}'".format(sys._getframe().f_code.co_name)
        return dt

    def get_user_secondary_data(self):
        secondary_data = {}
        try:
            secondary_data.update(self.get_user_additional_info())
            secondary_data.update(self.get_user_extra_data())
            secondary_data["wallposts"] = self.get_user_number_of_wallposts()
            secondary_data["photo"] = self.get_user_profile_photo_link()
        except Exception as e:
            print "Error in '{}'".format(sys._getframe().f_code.co_name)
        return secondary_data

    def get_user_additional_info(self):
        additional_info = {}
        short_profile_info = []
        for item in self.soup.findAll(class_='pinfo_row'):
            text = item.text
            if ':' in text:
                short_profile_info.append(text)

        for info_item in short_profile_info:
            item_title, item_value = info_item.split(":")
            item_title = item_title.lower().replace(" ", "_").strip()
            additional_info[item_title] = item_value

        for i, item in enumerate(self.soup.findAll(class_='pp_info')):
            text = item.text
            tmp = "Info {0}: {1}".format(i+1, text)
            short_profile_info.append(tmp)

        for info_item in short_profile_info:
            item_title, item_value = info_item.split(":")
            item_title = item_title.lower().replace(" ", "_").strip()
            additional_info[item_title] = item_value

        return additional_info

    def get_user_extra_data(self):
        # self.vk_logger.logger.debug(
        #     "Getting extra data (e.g. number of photos/communities)")
        data = {}
        extra_data = self.soup.findAll(class_='profile_menu')
        if extra_data:
            extra_data_list = []
            tmp_list = []
            for el in extra_data:
                for item in el.findAll(class_='pm_item'):
                    item = item.text.lower()
                    if 'show more' not in item:
                        extra_data_list.append(item)

        # self.vk_logger.logger.debug(
        #     "Parsing extra data (e.g. number of photos/communities)")
        for item in extra_data_list:
            item_parts = item.split(' ')
            key = ''
            value = ''
            for part in item_parts:
                if part.isdigit():
                    value = part
                else:
                    key += part + '_'
            key = key.replace('_', ' ').rstrip().replace(' ', '_')
            key = key.lower().replace(" ", "_").strip()
            data[key] = value

        return data

    def get_user_number_of_wallposts(self):
        # self.vk_logger.logger.debug("Getting number of wall posts")
        wallposts_number = -1
        all_slim_headers = self.soup.findAll(class_='slim_header')
        if len(all_slim_headers) > 0:
            for item in all_slim_headers:
                if 'post' in item.text:
                    number_of_wallposts = get_all_digits_from_str(item.text)
                    if str(number_of_wallposts).isdigit():
                        wallposts_number = number_of_wallposts
                    else:
                        break
        return wallposts_number

    def get_user_profile_photo_link(self):
        # self.vk_logger.logger.debug("Getting link to profile photo.")
        photo_link = None
        short_profile = self.soup.find(id="mcont")
        if short_profile:
            short_profile = short_profile.find(class_='owner_panel')
            if short_profile:
                photo_tag = short_profile.find('a')
                if photo_tag:
                    photo_link = photo_tag.get('href')
                    if photo_link:
                        photo_link = urlparse.urljoin(self.url,
                                                      photo_link)
        return photo_link
