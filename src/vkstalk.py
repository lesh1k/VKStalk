# -*- coding: utf-8 -*-

# Required modules
from __future__ import unicode_literals
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from logger import Logger
from utils import clear_screen, normalize_unicode
from parser import Parser
from models import *

import urllib2  # retrieve the page
import time  # used for time.sleep()
import string
import config
import sys


class VKStalk:

    def __init__(self, user_id, log_level=21, email_notifications=False, email=''):
        self.birth = datetime.now().strftime(config.DATETIME_FORMAT)

        self.db_session = Session()

        try:
            user = self.db_session.query(User).filter_by(vk_id=user_id).one()
        except NoResultFound, e:
            user = User(vk_id=user_id)
            self.db_session.add(user)
            self.db_session.commit()

        if not user.data:
            user.data = UserData()
            self.db_session.commit()
        self.user = user
        self.db_session.close()

        self.vk_logger = Logger(user_id, 10)

        self.version = "| VKStalk ver. {} |".format(config.VERSION)
        # pretify program version output
        self.version = '\n' + '=' * \
            ((42 - len(self.version)) / 2) + self.version + \
            '=' * ((42 - len(self.version)) / 2) + '\n\n'

        self.last_error = None
        self.error_counter = 0
        self.logs_counter = 0

        clear_screen()
        # Print greeting message
        self.vk_logger.console_log(
            "VKStalk successfully launched! Have a tea and analyze the results.")

    def populate_user(self):
        p = Parser(self.user.url)
        user_data = p.get_user_data()
        self.save_data_to_db(user_data)

    def save_data_to_db(self, user_data):
        try:
            changes = {
                'data': {},
                'activity_log': {},
            }

            keys = [i for i in user_data.keys() if i in self.user.data.__dict__.keys()]

            for key in keys:
                old_val = getattr(self.user.data, key)
                new_val = user_data[key]
                if (type(old_val) != type(new_val) and unicode(old_val) != unicode(new_val)) or (old_val != new_val and type(old_val) == type(new_val)):
                    changes['data'][key] = {
                        'old': old_val,
                        'new': new_val,
                    }
                    setattr(self.user.data, key, user_data[key])

            activity_log = UserActivityLog()
            if changes['data']:
                user_data_changes = generate_user_data_changes_string(changes['data'])
                activity_log.updates = user_data_changes.strip()
            keys = [i for i in user_data.keys() if i in UserActivityLog.__dict__.keys() and "__" not in i]
            for key in keys:
                if len(self.user.activity_logs):
                    old_val = getattr(self.user.activity_logs[-1], key)
                    new_val = user_data[key]

                    if (type(old_val) != type(new_val) and unicode(old_val) != unicode(new_val)) or (old_val != new_val and type(old_val) == type(new_val)):
                        changes['activity_log'][key] = {
                            'old': old_val,
                            'new': new_val,
                        }
                else:
                    changes['activity_log'] = {"First launch placeholder": True}
                setattr(activity_log, key, user_data[key])
            if changes['activity_log'] or activity_log.updates:
                if "last_visit" in changes['activity_log'] and len(changes['activity_log'].keys()) == 1:
                    pass
                else:
                    self.user.activity_logs.append(activity_log)
                    self.logs_counter += 1
        except:
            raise
            print "Error in '{}'".format(sys._getframe().f_code.co_name)
            print "Error setting key:value - {0}:{1}".format(key. user_data[key])
            self.db_session.rollback()
            print "Session changes were rolled back."
        finally:
            self.changes = changes
            self.db_session.commit()
            # self.db_session.close()

    # #####Logging part######
    def console_log(self):
        # self.vk_logger.logger.debug('Writing log to console')
        try:
            log = self.generate_console_log()
            self.vk_logger.console_log(log)
        except Exception as e:
            # self.vk_logger.logger.error(
            #     "Error in writing Data to log file and console")
            print "Error in '{}'".format(sys._getframe().f_code.co_name)

    def generate_console_log(self):
        # self.vk_logger.logger.debug('Preparing log')

        # Common log to file
        self.log = "{0} -- {1}\nStatus: {2}\n\n".format(self.user.data.name,
                                                        self.user.last_visit_text,
                                                        self.user.activity_logs[
                                                            -1].status
                                                        )

        # Generating a timestamp and adding it to the log string
        self.log_time = datetime.strftime(
            datetime.now(), '>>>Date: %d-%m-%Y. Time: %H:%M:%S\n')
        self.log = self.log_time + self.log.rstrip()
        self.log += generate_user_data_changes_string(self.changes['data'])
        self.log += '\n\n'

        # Prepare output to console
        console_log = config.CONSOLE_LOG_TEMPLATE.format(
            self.version,
            self.birth,
            self.user.vk_id,
            self.user.data.name,
            self.logs_counter,
            self.error_counter,
            self.log,
            self.last_error,
        )

        return console_log

    # ######################################END logging########################

    def single_request(self):
        # ConsoleLog('Fetching user data...')
        self.vk_logger.console_log('Fetching user data...')
        # self.vk_logger.logger.debug('Start single request')
        self.db_session = Session()
        self.db_session.add(self.user)
        self.populate_user()
        clear_screen()
        self.console_log()
        self.db_session.close()

        # self.vk_logger.logger.debug('Finished single request\n\n')

    def work(self):
        # self.vk_logger.logger.debug('Begin work')
        while True:
            self.single_request()
            time.sleep(config.DATA_FETCH_INTERVAL)


def generate_user_data_changes_string(data_changes):
    updates = ""

    if data_changes:
        for key in data_changes:
            title = key.replace("_", " ").capitalize()
            old_val = data_changes[key]['old']
            new_val = data_changes[key]['new']
            updates += "\n{0}: {1} => {2}".format(title, old_val, new_val)

    return updates
