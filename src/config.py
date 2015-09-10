# -*- coding: utf-8 -*-

import os

VERSION = "4.0.1"  # this should be extracted when packaging the app

PROJECT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir))


# Logs
DATA_FOLDER_NAME = "data (beta)"
USER_ACTIVITY_FOLDER_NAME = "activity"  # where collected data about a user will be stored
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


DATETIME_FORMAT = "%d-%B-%Y at %H:%M"

DATA_FETCH_INTERVAL = 15  # seconds

MAIL_NOTIFICATION_HOURS = [10, 23]  # hours

REPORT_DAYS = [6]  # day of week
REPORT_HOURS = [10]  # hours

MAX_FILES_PER_REPORT = 8
