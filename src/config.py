# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from secrets import *

VERSION = "4.0.1"  # this should be extracted when packaging the app

PROJECT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir))


# Logs
DATA_FOLDER_NAME = "data (beta)"
# where collected data about a user will be stored
USER_ACTIVITY_FOLDER_NAME = "activity"
LOGS_FOLDER_NAME = "logs"
SUMMARY_FOLDER_NAME = "summaries"
ARCHIVE_FOLDER_NAME = "archive"

DATA_PATH = os.path.join(PROJECT_PATH, DATA_FOLDER_NAME)
USER_PATH = os.path.join(DATA_PATH, "user_{}")

USER_ACTIVITY_LOGS_PATH = os.path.join(USER_PATH, USER_ACTIVITY_FOLDER_NAME)
LOGS_PATH = os.path.join(USER_PATH, LOGS_FOLDER_NAME)
SUMMARY_LOGS_PATH = os.path.join(USER_PATH, SUMMARY_FOLDER_NAME)
ARCHIVE_PATH = os.path.join(USER_PATH, ARCHIVE_FOLDER_NAME)
LOGS_DIRECTORIES = (DATA_PATH, USER_PATH, USER_ACTIVITY_LOGS_PATH, LOGS_PATH,
                    SUMMARY_LOGS_PATH, ARCHIVE_PATH,)

# self.version, self.birth, self.user_id, self.user_data['name'],
# self.logs_counter, self.error_counter, self.log, self.last_error
CONSOLE_LOG_TEMPLATE = (
    "{0}Launched on {1}\nUser ID: {2}\nUser Name: {3}" +
    "\nLogs written: {4}\nErrors occurred: {5}\n\n" +
    "=" * 14 + "| LATEST LOG |" + "=" * 14 + "\n\n{6}" +
    "=" * 14 + "| LAST ERROR |" + "=" * 14 + "\n\n{7}"
)

ACTIVITY_LOGS_ROTATE_INTERVAL = 1
ACTIVITY_LOGS_ROTATE_WHEN = "midnight"
LOGS_ROTATE_INTERVAL = 1
LOGS_ROTATE_WHEN = "midnight"


SOURCE_URL = "http://vk.com"


DATETIME_FORMAT = "%d-%B-%Y at %H:%M"

DATA_FETCH_INTERVAL = 15  # seconds

MAIL_NOTIFICATION_HOURS = [10, 23]  # hours

REPORT_DAYS = [6]  # day of week
REPORT_HOURS = [10]  # hours

MAX_FILES_PER_REPORT = 8

MAX_CONNECTION_ATTEMPTS = 10

VK_TZ = "Europe/Moscow"
CLIENT_TZ = "Europe/Chisinau"
