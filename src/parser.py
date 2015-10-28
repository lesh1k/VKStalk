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
from utils import clear_screen, normalize_unicode


class Parser:
    def __init__(self):
        pass

    def cook_soup(self):
        # Return the soup obtained from scrapping the page or False if any
        # error occured while connecting

        # requesting the page
        self.vk_logger.logger.debug('Fetching HTML page')

        try:
            connection_handle = urllib2.urlopen(self.user.url, timeout=20)
            html = connection_handle.read()
            connection_handle.close()
        except Exception as e:
            self.vk_logger.logger.error(
                "Could not fetch HTML page. Retrying in 7 seconds...")
            self.vk_logger.logger.debug("Restarting request")
            # self.HandleError(
            #     step='Fetching HTML page.',
            #     exception_msg=e,
            #     dump_vars=True,
            #     console_msg='Could not fetch HTML page. Retrying in 7 seconds...',
            #     sleep=7,
            #     debug_msg='Restarting request.'
            # )
            return False

        # set soup
        self.vk_logger.logger.debug('Cooking soup')
        self.soup = BeautifulSoup(html)
        self.vk_logger.logger.debug('Cooking soup finished')

        return True

    def GetUserData(self):
        # Returns a dictionary with user data
        # The following data is available depending on user-specific
        # security settings: name, photo, isOnline or last visited time,
        # skype, instagram, facebook, phone_number, university, number
        # of photos, nr of posts on the wall, nr. of audio files, nr. of
        # online friends, some of the friends who are online, nr. of friends
        # nr. of gifts. Some more data is much less relevant.

        # Check if the profile is not hidden. Page was deleted or does not
        # exist
        max_attempts = config.MAX_CONNECTION_ATTEMPTS
        for attempt in xrange(1, max_attempts + 1):
            self.vk_logger.logger.debug(
                "Checking if the profile exists and is accessible." +
                "Attempt ({0} of {1})".format(attempt, max_attempts))
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
                self.CookSoup()
                profile_private = True
            else:
                self.vk_logger.logger.debug('Profile PUBLIC. OK!')
                profile_private = False
                break
        if profile_private:
            # self.SendMail(
            # mail_type='error', msg="Execution terminated! Private profile.
            # Access forbidden.")
            exit("Private profile. Access forbidden")

        # self.vk_logger.logger.debug("Initializing user_data with default values")
        # Initialize user_data dictionary with default values
        # user_data = {}
        # Primary data
        # user_data['name'] = '_not_found'
        # user_data['status'] = '_not_found'
        # user_data['online'] = '_not_found'
        # user_data['last_visit'] = '_not_found'
        # user_data['mobile_version'] = False
        # Secondary data
        # user_data['skype'] = '_not_found'
        # user_data['site'] = '_not_found'
        # user_data['twitter'] = '_not_found'
        # user_data['instagram'] = '_not_found'
        # user_data['facebook'] = '_not_found'
        # user_data['phone'] = '_not_found'
        # user_data['university'] = '_not_found'
        # user_data['photo'] = '_not_found'
        # user_data['birthday'] = '_not_found'
        # user_data['hometown'] = '_not_found'
        # user_data['current_city'] = '_not_found'
        # other secondary data entries are added during runtime. These depend
        # on the profile of the user.
        # self.secondary_data_keys_list = []

        # if self.debug_mode:
        #     WriteDebugLog('Done', userid=self.user_id)

        #:Data fetching
        self.vk_logger.logger.debug("Start data fetching")
        # :Name
        self.vk_logger.logger.debug("Obtaining username")
        try:
            self.user.name = self.soup.html.head.title.text
            # normalize_unicode(self.user)
            # for filename verification
            valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

            # Sanitize user name
            for c in self.user.name:
                if c not in valid_chars:
                    self.user.name = self.user.name.replace(c, '')
            if self.user.name[-2:] == 'VK':
                self.user.name = self.user.name[:-2].rstrip()
        except Exception as e:
            self.vk_logger.logger.error("Trouble getting username")
            exit()
            # self.HandleError(
            #     step='Setting username.', exception_msg=e, dump_vars=True)
            return False

        # :Status
        self.vk_logger.logger.debug('Obtaining user status')
        status = self.soup.find('div', {"class": "status"})
        if status:
            self.user.status = status.text
        else:
            status = self.soup.find('div', {'class': 'pp_status'})
            if status:
                self.user.status = status.text

        # :Mobile version or not
        self.vk_logger.logger.debug(
            "Determining if user is logged in from a mobile device.")
        try:
            # alt: self.soup.find('b',{'class':'lvi mlvi'})
            if self.soup.find(class_='mlvi') is not None:
                self.user.mobile_version = True
        except Exception as e:
            # self.HandleError(
            # step='Determining if user is logged in from a mobile device.',
            # exception_msg=e, dump_vars=True)
            return False

        # :Online OR not [last seen time]
        self.vk_logger.logger.debug(
            "Obtaining info about user ONLINE status (online/offline)")
        try:
            # If no concrete message for user being offline. Thus, will assume
            # that if last seen time is not found, the user is Online
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

            if last_seen and last_seen != '':
                self.user.online = False
                date_found = False
                self.user.last_visit = last_seen
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
                            self.user.last_visit = date_time.strftime(
                                "last seen on %B %d at %H:%M")
                        except Exception as e:
                            # self.HandleError(
                            # step="Parsing date/time in last_seen.",
                            # exception_msg=e, dump_vars=True)
                            return False
                    else:
                        try:
                            date_time = datetime.strptime(
                                last_seen[last_seen.find('at'):], "at %I:%M %p")
                            # By default year is 1900 and if time 00.41, minus delta it gets year
                            # 1899 and raises an error
                            date_time = date_time.replace(
                                year=datetime.now().year)
                            date_time = date_time - time_delta
                            self.user.last_visit = 'last seen {}'.format(
                                date_time.strftime(
                                    last_seen[:last_seen.find('at')] +
                                    "at %H:%M")
                            )
                            if (('yesterday' in last_seen) and
                                    (datetime.now().hour - hours_delta < 0)):
                                self.user.last_visit = user_data[
                                    'last_visit'].replace('yesterday', 'today')
                            elif (('yesterday' in last_seen) and
                                  (datetime.now().hour - hours_delta >= 0) and
                                    (date_time.hour + hours_delta >= 24)):
                                self.user.last_visit = self.user.last_visit.replace(
                                    'yesterday',
                                    'two days ago')
                            elif (('today' in last_seen) and
                                  (date_time.hour + hours_delta >= 24)):
                                self.user.last_visit = self.user.last_visit.replace(
                                    'today', 'yesterday')
                        except Exception as e:
                            # self.HandleError(
                            # step="Parsing time in last_seen",
                            # exception_msg=e, dump_vars=True)
                            return False

                elif last_seen.lower() == 'online':
                    self.user.online = True
                    self.user.last_visit = 'Online'

                else:  # print raw last_seen data
                    # +' That is raw data!'
                    self.user.last_visit = 'last seen ' + last_seen
            else:
                self.user.online = True
                self.user.last_visit = 'Online'

            if self.user.mobile_version:
                self.user.last_visit += ' [Mobile]'

        except Exception as e:
            # self.HandleError(
            # step="Determining user's online status.", exception_msg=e,
            # dump_vars=True)
            return False

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