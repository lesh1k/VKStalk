# -*- coding: utf-8 -*-

# Required modules
from __future__ import unicode_literals
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from helpers.h_logging import get_logger
from helpers.utils import clear_screen, as_client_tz
from core.parser import Parser
from core.models import *
from config import settings

import time  # used for time.sleep()
import sys


class VKStalk:

    def __init__(self, user_id, log_level=21, email_notifications=False, email=''):
        get_logger('file').info('Initializing VKStalk')
        self.birth = datetime.now().strftime(settings.DATETIME_FORMAT)
        self.user = User.get_or_create_user_with_vk_id(user_id)
        self.logs_counter = 0
        clear_screen()

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

            keys = set(user_data.keys()) & set(self.user.data.__dict__.keys())

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
        except Exception, e:
            get_logger('file').fatal(
                "Error in '{}'".format(sys._getframe().f_code.co_name))
            get_logger('file').fatal(
                "Error setting key:value - {0}:{1}".format(key. user_data[key]))
            self.db_session.rollback()
            get_logger('file').info("Session changes were rolled back.")
            raise
        finally:
            self.changes = changes
            self.db_session.commit()

    # #####Logging part######
    def console_log(self):
        log = self.generate_console_log()
        get_logger('console').info(log)

    def generate_console_log(self):
        log_tmpl = "{0} -- {1}\nStatus: {2}\n\n"
        self.log = log_tmpl.format(self.user.data.name,
                                   self.user.last_visit_text,
                                   self.user.activity_logs[-1].status,
                                   )

        # Generating a timestamp and adding it to the log string
        dt_client_now = pytz.timezone(settings.SERVER_TZ).localize(datetime.now())
        dt_client_now = as_client_tz(dt_client_now)
        check_time = datetime.strftime(dt_client_now, settings.LOG_CHECKED_TMPL)

        dt_log_timestamp = self.user.activity_logs[-1].timestamp
        dt_log_timestamp = as_client_tz(dt_log_timestamp)
        log_time = datetime.strftime(dt_log_timestamp, settings.LOG_DATETIME_TMPL)

        self.log = check_time + log_time + self.log.rstrip()
        self.log += generate_user_data_changes_string(self.changes['data'])
        self.log += '\n\n'

        # Prepare output to console
        console_log = settings.CONSOLE_LOG_TEMPLATE.format(
            self.birth,
            self.user.vk_id,
            self.user.data.name,
            self.logs_counter,
            self.log
        )

        return console_log

    # ######################################END logging########################

    def single_request(self):
        get_logger('console').info('Fetching user data...')
        self.db_session = Session()
        self.db_session.add(self.user)
        self.populate_user()
        clear_screen()
        self.console_log()
        self.db_session.close()

    def work(self):
        while True:
            self.single_request()
            time.sleep(settings.DATA_FETCH_INTERVAL)


def generate_user_data_changes_string(data_changes):
    updates = ""

    if data_changes:
        for key in data_changes:
            title = key.replace("_", " ").capitalize()
            old_val = data_changes[key]['old']
            new_val = data_changes[key]['new']
            updates += "\n{0}: {1} => {2}".format(title, old_val, new_val)

    return updates
