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
# from utils import clear_screen, normalize_unicode


class Parser:
    def __init__(self):
        self.user = {}

    def cook_soup(self):
        # Return the soup obtained from scrapping the page or False if any
        # error occured while connecting

        # set soup
        # self.vk_logger.logger.debug('Cooking soup')
        if self.fetch_html():
            self.soup = BeautifulSoup(self.html)
        else:
            return False
        # self.vk_logger.logger.debug('Cooking soup finished')

        return True

    def fetch_html(self):
        # requesting the page
        # self.vk_logger.logger.debug('Fetching HTML page')

        try:
            cHandle = urllib2.urlopen(self.user.url, timeout=20)
            self.html = cHandle.read()
            cHandle.close()
        except Exception as e:
            # self.vk_logger.logger.error(
                # "Could not fetch HTML page. Retrying in 7 seconds...")
            # self.vk_logger.logger.debug("Restarting request")
            # self.HandleError(
            #     step='Fetching HTML page.',
            #     exception_msg=e,
            #     dump_vars=True,
            #     console_msg='Could not fetch HTML page. Retrying in 7 seconds...',
            #     sleep=7,
            #     debug_msg='Restarting request.'
            # )
            return False

        return True

    def get_user_data(self):
        # Check if the profile is not hidden. Page was deleted or does not
        # exist
        if self.is_profile_private():
            # self.SendMail(
            # mail_type='error', msg="Execution terminated! Private profile.
            # Access forbidden.")
            exit("Private profile. Access forbidden")

        #:Data fetching
        # self.vk_logger.logger.debug("Start data fetching")
        # :Name
        self.user["name"] = self.get_user_name()

        # :Status
        self.user["status"] = self.get_user_status()

        # :Mobile version or not
        self.user["mobile_version"] = self.is_user_mobile()

        # :Online OR not [last seen time]
        self.user["online"] = self.is_user_online()

        # Secondary data fectching
        try:
            current_step = "Fetching secondary data"
            secondary_data_names_list = ['Skype', 'Twitter', 'Instagram', 'University',
                                         'Birthday', 'Facebook', 'Website', 'Phone', 'Hometown', 'Current city']
            self.short_profile_info = []

            self.vk_logger.logger.debug("Parsing 'pinfo_row'")
            for item in self.soup.findAll(class_='pinfo_row'):
                text = item.text
                if ':' in text:
                    self.short_profile_info.append(text)

            self.vk_logger.logger.debug("Saving parsed data to 'user' instance")
            for info_item in self.short_profile_info:
                item_title, item_value = info_item.split(":")
                setattr(self.user, item_title.lower().replace(" ", "_").strip(),
                        item_value)

            self.vk_logger.logger.debug(
                "Getting extra data (e.g. number of photos/communities)")
            extra_data = self.soup.find(class_='profile_menu')
            if extra_data:
                extra_data_list = []
                extra_data = extra_data.findAll(class_='pm_item')
                for item in extra_data:
                    item = item.text.lower()
                    if 'show more' not in item:
                        extra_data_list.append(item)

            self.vk_logger.logger.debug(
                "Parsing extra data (e.g. number of photos/communities)")
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
                # self.secondary_data_keys_list.append(key)
                # user_data[key] = value
                setattr(
                    self.user, key.lower().replace(" ", "_").strip(), value)

            self.vk_logger.logger.debug("Getting number of wall posts")
            all_slim_headers = self.soup.findAll(class_='slim_header')
            if len(all_slim_headers) > 0:
                for item in all_slim_headers:
                    if 'post' in item.text:
                        number_of_wallposts = item.text.split()[0]
                        # number_of_wallposts = number_of_wallposts.encode(
                        #     'ascii', 'ignore')
                        # clear number from punctuation
                        # table = string.maketrans("", "")
                        # number_of_wallposts = number_of_wallposts.translate(
                        #     table, string.punctuation)
                        if str(number_of_wallposts).isdigit():
                            self.user.number_of_wallposts = number_of_wallposts
                            # self.secondary_data_keys_list.append(
                            #     'number_of_wallposts')
                        else:
                            break

            self.vk_logger.logger.debug("Getting link to profile photo.")
            short_profile = self.soup.find(id="mcont")
            if short_profile:
                short_profile = short_profile.find(class_='owner_panel')
                if short_profile:
                    photo_tag = short_profile.find('a')
                    if photo_tag:
                        photo_link = photo_tag.get('href')
                        if photo_link:
                            self.user.photo = urlparse.urljoin(self.user.url,
                                                               photo_link)
                            # self.secondary_data_keys_list.append('photo')

        except Exception as e:
            self.vk_logger.logger.error(
                "Got into an error in secondary data fetching and parsing." +
                "ERR: {}".format(e))
            # self.HandleError(
            # step=current_step, exception_msg=e, dump_vars=True,
            # debug_msg=current_step)
            return False

        # set object user_data
        # self.user_data = user_data
        return True

    def is_profile_private(self):
        max_attempts = config.MAX_CONNECTION_ATTEMPTS
        for attempt in xrange(1, max_attempts + 1):
            # self.vk_logger.logger.debug(
            #     "Checking if the profile exists and is accessible." +
            #     "Attempt ({0} of {1})".format(attempt, max_attempts))
            if ((self.soup.find('div', {'class': 'service_msg_null'}))
                    or ('This user deleted their page. Information unavailable.' in self.soup.text)
                    or ('This page is either deleted or has not been created yet.' in self.soup.text)):
                clear_screen()
                # self.HandleError(
                #     step='Verifying if profile is accessible. Attempt (' + str(
                #         attempt + 1) + ' of ' + str(max_attempts) + ')',
                #     exception_msg='Access forbidden. Profile PRIVATE or page does not exist.',
                #     debug_msg='Access forbidden. Profile PRIVATE or page does not exist. Attempt (' + str(
                #         attempt + 1) + ' of ' + str(max_attempts) + ')',
                #     sleep=15,
                #     console_msg=(
                #         'Access forbidden. Profile PRIVATE or page does not exist.\nAttempt ('
                #         + str(attempt + 1) + ' of ' +
                #         str(max_attempts) + ').\nRetry in 15 seconds...\n'
                #     )
                # )
                # ConsoleLog('Fetching user data...')
                self.cook_soup()
                profile_private = True
            else:
                # self.vk_logger.logger.debug('Profile PUBLIC. OK!')
                profile_private = False
                break

        return profile_private

    def get_user_name(self):
        # self.vk_logger.logger.debug("Obtaining username")
        try:
            username = self.soup.html.head.title.text
            # normalize_unicode(self.user)
            # for filename verification
            valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

            # Sanitize user name
            for c in username:
                if c not in valid_chars:
                    username = username.replace(c, '')
            if username[-2:] == 'VK':
                username = username[:-2].rstrip()
        except Exception as e:
            # self.vk_logger.logger.error("Trouble getting username")
            # exit()
            # self.HandleError(
            #     step='Setting username.', exception_msg=e, dump_vars=True)
            pass
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
        # self.vk_logger.logger.debug(
        #     "Determining if user is logged in from a mobile device.")
        try:
            # alt: self.soup.find('b',{'class':'lvi mlvi'})
            if self.soup.find(class_='mlvi') is not None:
                is_mobile = True
            return is_mobile
        except Exception as e:
            # self.HandleError(
            # step='Determining if user is logged in from a mobile device.',
            # exception_msg=e, dump_vars=True)
            pass

    def is_user_online(self):
        is_online = True
        # self.vk_logger.logger.debug(
        #     "Obtaining info about user ONLINE status (online/offline)")
        try:
            # If no concrete message for user being offline. Thus, will assume
            # that if last seen time is not found, the user is Online
            last_seen = self.get_user_last_seen_text(self)

            if last_seen and last_seen != '':
                is_online = False
                if last_seen.lower() == 'online':
                    is_online = True

        except Exception as e:
            # self.HandleError(
            # step="Determining user's online status.", exception_msg=e,
            # dump_vars=True)
            pass

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
