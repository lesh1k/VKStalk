# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import logging
from secrets import *
from helpers.program_version import prettify_project_version


PROJECT_NAME = "vkstalk"
VERSION = "5.0.0 ALPHA"  # this should be extracted when packaging the app
VERSION_PRETTIFIED = prettify_project_version(VERSION)

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))


SOURCE_URL = "http://vk.com"
DATA_FETCH_INTERVAL = 15  # seconds
DATETIME_FORMAT = "%d-%B-%Y at %H:%M"


MAIL_NOTIFICATION_HOURS = [10, 23]  # hours

REPORT_DAYS = [6]  # day of week
REPORT_HOURS = [10]  # hours

MAX_FILES_PER_REPORT = 8

MAX_CONNECTION_ATTEMPTS = 10
CONNECTION_TIMEOUT = 20  # seconds


# Timezones
VK_TZ = "Europe/Moscow"
CLIENT_TZ = "Europe/Chisinau"


# Logging

# self.birth, self.user_id, self.user_data['name'],
# self.logs_counter, self.error_counter, self.log, self.last_error
CONSOLE_LOG_TEMPLATE = (
    VERSION_PRETTIFIED +
    "Launched on {0}\nUser ID: {1}\nUser Name: {2}" +
    "\nLogs written: {3}\nErrors occurred: {4}\n\n" +
    "=" * 14 + "| LATEST LOG |" + "=" * 14 + "\n\n{5}" +
    "=" * 14 + "| LAST ERROR |" + "=" * 14 + "\n\n{6}"
)

LOGS_ROTATE_INTERVAL = 1
LOGS_ROTATE_WHEN = "midnight"

LOGS_PATH = os.path.join(PROJECT_ROOT, "logs")
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'message': {
            'format': '%(message)s',
        },
        'verbose': {
            'format': '%(levelname)s: [%(asctime)s] [%(module)s %(process)d] %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'message',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOGS_PATH, "vkstalk.log"),
            'when': LOGS_ROTATE_WHEN,
            'interval': LOGS_ROTATE_INTERVAL,
            'formatter': 'verbose',
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOGS_PATH, "error.log"),
            'when': LOGS_ROTATE_WHEN,
            'interval': LOGS_ROTATE_INTERVAL,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '{}.console'.format(PROJECT_NAME): {
            'handlers': ['console'],
            'level': 'INFO'
        },
        '{}.file'.format(PROJECT_NAME): {
            'handlers': ['file', 'error'],
            'level': 'DEBUG',
        },
    },
}
