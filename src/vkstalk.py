# -*- coding: utf-8 -*-

# Required modules
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
from user import User as UserObj
import config
import urlparse
import sys
from utils import clear_screen, normalize_unicode
from parser import Parser
from models import *


class VKStalk:

    def __init__(self, user_id, log_level=21, email_notifications=False, email=''):
        self.birth = datetime.now().strftime(config.DATETIME_FORMAT)

        self.db_session = Session()

        user = self.db_session.query(User).filter_by(vk_id=user_id).first()
        if not user:
            user = User(vk_id=user_id)
            self.db_session.add(user)
            self.db_session.commit()
        if not user.data:
            user.data = UserData()
            self.db_session.commit()
        self.user = user

        self.vk_logger = Logger(user_id, 10)

        self.version = "| VKStalk ver. {} |".format(config.VERSION)
        # pretify program version output
        self.version = '\n' + '=' * \
            ((42 - len(self.version)) / 2) + self.version + \
            '=' * ((42 - len(self.version)) / 2) + '\n\n'

        # self.mail_notification_hours = config.MAIL_NOTIFICATION_HOURS
        # self.summary_notification_days = config.REPORT_DAYS
        # self.summary_notification_hours = config.REPORT_HOURS
        # self.max_files_for_summary = config.MAX_FILES_PER_REPORT

        self.prev_log = ''
        self.log = ''
        self.last_error = None
        self.error_counter = 0
        self.logs_counter = 0

        # self.data_logger_is_built = False
        # self.error_logger_is_built = False
        # self.debug_mode = debug_mode
        # self.current_path = '/'.join(__file__.split('/')[:-1])
        # self.filename = ''
        # self.secondary_data_keys_list = []
        self.email_notifications = email_notifications
        self.mail_recipient = email
        self.last_mail_time = -1
        self.last_summary_mail_day = -1
        # 7 will consider Mon-Sun. 8 for Sun-Sun, so that data saved on sunday
        # after 10AM is also considered

        self.prev_photo_change = None
        self.prev_photos_with_change = None

        clear_screen()
        # Print greeting message
        self.vk_logger.console_log(
            "VKStalk successfully launched! Have a tea and analyze the results.")

    def PrepareLog(self):
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
        self.console_log = config.CONSOLE_LOG_TEMPLATE.format(
            self.version,
            self.birth,
            self.user.vk_id,
            self.user.data.name,
            self.logs_counter,
            self.error_counter,
            self.log,
            self.last_error,
        )

        # mailer.send_mail_if_time()

        clear_screen()
        # return write_log
        return True

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
    def ShowWriteInfo(self):
        if self.PrepareLog():
            # self.vk_logger.logger.debug('Writing log to file')
            try:
                # self.vk_logger.log_activity(self.log)
                self.vk_logger.console_log(self.console_log)
                pass
            except Exception as e:
                # self.vk_logger.logger.error(
                #     "Error in writing Data to log file and console")
                return False

        return True

    # ######################################END logging########################

    # Summarizer
    # Send summaries by email, every Sunday at 9AM
    def Summarize(self):

        pass

    ##########################################################################

    def SingleRequest(self):
        # ConsoleLog('Fetching user data...')
        self.vk_logger.console_log('Fetching user data...')
        # self.vk_logger.logger.debug('Start single request')
        self.populate_user()

        clear_screen()
        if not self.ShowWriteInfo():
            return False

        # self.vk_logger.logger.debug('Finished single request\n\n')

    def Work(self):
        # self.vk_logger.logger.debug('Begin work')
        while True:
            if self.SingleRequest() == False:
                break
            time.sleep(config.DATA_FETCH_INTERVAL)
        ##RESTART APP###
        clear_screen()
        # Restart main cycle
        self.Work()


def generate_user_data_changes_string(data_changes):
    updates = ""

    if data_changes:
        for key in data_changes:
            title = key.replace("_", " ").capitalize()
            old_val = data_changes[key]['old']
            new_val = data_changes[key]['new']
            updates += "\n{0}: {1} => {2}".format(title, old_val, new_val)

    return updates
