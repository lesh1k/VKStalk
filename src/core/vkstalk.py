# -*- coding: utf-8 -*-

# Required modules
from __future__ import unicode_literals
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from helpers.h_logging import get_logger
from helpers.utils import clear_screen, as_client_tz, make_data_updates_string
from core.parser import Parser
from core.models import *
from config import settings

import time  # used for time.sleep()
import sys


class VKStalk:

    def __init__(self, user_id):
        get_logger('file').info('Initializing VKStalk')
        self.birth = datetime.now().strftime(settings.DATETIME_FORMAT)
        self.user = User.from_vk_id(user_id)
        self.logs_counter = 0
        clear_screen()

    def scrape(self):
        while True:
            self.single_request()
            time.sleep(settings.DATA_FETCH_INTERVAL)

    def single_request(self):
        get_logger('console').info('Fetching user data...')
        self.db_session = Session()
        self.db_session.add(self.user)
        data = self.parse_user_data()
        self.store_user_data(data)
        self.console_log()
        self.db_session.close()

    def parse_user_data(self):
        p = Parser(self.user.url)
        user_data = p.get_user_data()
        return user_data

    def store_user_data(self, user_data):
        try:
            changes = {}
            changes['data'] = UserData.get_diff(self.user.data,
                                                UserData.from_dict(user_data))
            for key in changes['data']:
                setattr(self.user.data, key, changes['data'][key]['new'])

            activity_log = UserActivityLog.from_dict(user_data)
            if changes['data']:
                user_data_changes = make_data_updates_string(changes['data'])
                activity_log.updates = user_data_changes.strip()
            if self.user.activity_logs:
                changes['activity_log'] = UserActivityLog.get_diff(
                    self.user.activity_logs[-1],
                    activity_log
                )
            if changes['data'] or changes['activity_log']:
                if "last_visit" not in changes['activity_log'] \
                   or len(changes['activity_log'].keys()) > 1:
                    self.user.activity_logs.append(activity_log)
                    self.logs_counter += 1
        except Exception, e:
            func_name = sys._getframe().f_code.co_name
            message = "Error in '{0}. Exception: {1}'".format(func_name, e)
            get_logger('file').fatal(message)
            self.db_session.rollback()
            get_logger('file').info("Session changes were rolled back.")
            raise
        finally:
            self.db_session.commit()

    def console_log(self):
        log = self.generate_console_log()
        clear_screen()
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
        updates = self.user.activity_logs[-1].updates
        if updates:
            self.log += '\n' + updates
        self.log += '\n\n'

        console_log = settings.CONSOLE_LOG_TEMPLATE.format(
            self.birth,
            self.user.vk_id,
            self.user.data.name,
            self.logs_counter,
            self.log
        )

        return console_log
