# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import urllib2  # retrieve the page
import codecs  # to encode into utf-8 russian characters
import time  # used for time.sleep()
import os  # to check if a file exists
from bs4 import BeautifulSoup
# from threading import Thread
import string
from datetime import datetime, timedelta
from pprint import pprint
from logger import Logger, Summarize
import smtplib  # for mail sending
from user import User
import config
import urlparse
import sys
from utils import clear_screen


class Parser:
    def __init__(self, url):
        self.user = {}
        self.url = url
        self.cook_soup()

    def cook_soup(self):
        if self.fetch_html():
            self.soup = BeautifulSoup(self.html)
        else:
            return False

        return True

    def fetch_html(self):
        try:
            cHandle = urllib2.urlopen(self.url, timeout=20)
            self.html = cHandle.read()
            cHandle.close()
        except Exception as e:
            print "Error in '{}'".format(sys._getframe().f_code.co_name)

        return True

    def get_user_data(self):
        if self.is_profile_private():
            exit("Private profile. Access forbidden")

        # :Data fetching
        # :Name
        self.user["name"] = self.get_user_name()

        # :Status
        self.user["status"] = self.get_user_status()

        # :Mobile version or not
        self.user["mobile_version"] = self.is_user_mobile()

        # :Online OR not [last seen time]
        self.user["online"] = self.is_user_online()
        self.user["last_visit"] = self.generate_user_last_seen_line()

        # :Secondary data fectching
        user_secondary_data = self.get_user_secondary_data()
        self.user.update(user_secondary_data)

        return self.user

    def is_profile_private(self):
        max_attempts = config.MAX_CONNECTION_ATTEMPTS
        for attempt in xrange(1, max_attempts + 1):
            if ((self.soup.find('div', {'class': 'service_msg_null'}))
                    or ('This user deleted their page. Information unavailable.' in self.soup.text)
                    or ('This page is either deleted or has not been created yet.' in self.soup.text)):
                clear_screen()
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
            # for filename verification
            valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

            # Sanitize user name
            for c in username:
                if c not in valid_chars:
                    username = username.replace(c, '')
            if username[-2:] == 'VK':
                username = username[:-2].rstrip()
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
        is_online = True
        try:
            # If no concrete message for user being offline. Thus, will assume
            # that if last seen time is not found, the user is Online
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
        return last_seen

    def generate_user_last_seen_line(self):
        date_found = False
        last_seen_line = None
        last_seen = self.get_user_last_seen_text()
        if last_seen and last_seen != '':
            last_seen = last_seen.replace('last seen ', '')

            if ('am' in last_seen) or ('pm' in last_seen):
                # Set timedelta according to daylight savings time
                if time.localtime().tm_isdst == 1:
                    hours_delta = 1
                    time_delta = timedelta(hours=hours_delta)
                else:
                    hours_delta = 2
                    time_delta = timedelta(hours=hours_delta)

                for c in last_seen[:last_seen.find('at')]:
                    if c.isdigit():
                        date_found = True
                        break
                if date_found:
                    try:
                        date_time = datetime.strptime(
                            last_seen, "%d %B at %I:%M %p")
                        # By default year is 1900 and if time 00.41, minus delta it gets year
                        # 1899 and raises an error
                        date_time = date_time.replace(
                            year=datetime.now().year)
                        date_time = date_time - time_delta
                        last_seen_line = date_time.strftime(
                            "last seen on %B %d at %H:%M")
                    except Exception as e:
                        print "Error in '{}'".format(sys._getframe().f_code.co_name)
                else:
                    try:
                        date_time = datetime.strptime(
                            last_seen[last_seen.find('at'):], "at %I:%M %p")
                        # By default year is 1900 and if time 00.41, minus delta it gets year
                        # 1899 and raises an error
                        date_time = date_time.replace(
                            year=datetime.now().year)
                        date_time = date_time - time_delta
                        last_seen_line = 'last seen {}'.format(
                            date_time.strftime(
                                last_seen[:last_seen.find('at')] +
                                "at %H:%M")
                        )
                        if (('yesterday' in last_seen) and
                                (datetime.now().hour - hours_delta < 0)):
                            last_seen_line = last_seen_line.replace('yesterday', 'today')
                        elif (('yesterday' in last_seen) and
                              (datetime.now().hour - hours_delta >= 0) and
                                (date_time.hour + hours_delta >= 24)):
                            last_seen_line = last_seen_line.replace(
                                'yesterday',
                                'two days ago')
                        elif (('today' in last_seen) and
                              (date_time.hour + hours_delta >= 24)):
                            last_seen_line = last_seen_line.replace(
                                'today', 'yesterday')
                    except Exception as e:
                        print "Error in '{}'".format(sys._getframe().f_code.co_name)

            elif last_seen.lower() == 'online':
                last_seen_line = 'Online'

            else:  # print raw last_seen data
                # +' That is raw data!'
                last_seen_line = 'last seen ' + last_seen
        else:
            last_seen_line = 'Online'

        if self.user["mobile_version"]:
            last_seen_line += ' [Mobile]'

        return last_seen_line

    def get_user_secondary_data(self):
        secondary_data = {}
        try:
            secondary_data.update(self.get_user_additional_info())
            secondary_data.update(self.get_user_extra_data())
            secondary_data["number_of_wallposts"] = self.get_user_number_of_wallposts()
            secondary_data["photo"] = self.get_user_profile_photo_link()
        except Exception as e:
            print "Error in '{}'".format(sys._getframe().f_code.co_name)
        return secondary_data

    def get_user_additional_info(self):
        additional_info = {}
        short_profile_info = []
        for item in self.soup.findAll(class_='miniblock'):
            text = item.text
            if ':' in text:
                short_profile_info.append(text)

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
                    number_of_wallposts = item.text.split()[0]
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
