from __future__ import unicode_literals
from config import settings
from datetime import datetime, timedelta
from tabulate import tabulate
from helpers.utils import as_client_tz, write_to_file
from models import *

import pytz
import os


def summary(user_id, max_days=settings.DEFAULT_SUMMARY_PERIOD,
            to_file=True, to_console=True):
    user = User.get_by_vk_id(user_id)
    if not user:
        print "No data on available on user with ID: {}".format(user_id)
        return None
    setup_summarizer()
    period = get_period(max_days)
    summary = make_summary(user_id, **period)
    if to_console:
        print summary
    if to_file:
        user_name = user.get_name()
        path = generate_summary_path(user_name, period)
        write_to_file(path, summary, mode="wb")
        print "Summary saved to: {}".format(path)


def setup_summarizer():
    try:
        os.mkdir(settings.SUMMARIES_PATH)
    except OSError as e:
        if e.errno != 17:  # (17, 'File exists')
            raise


def make_summary(user_id, start, end):
    user = User.from_vk_id(user_id)
    entries = user.activity_for(start, end)
    summary = tabulate(entries)
    return summary


def get_period(max_days=settings.DEFAULT_SUMMARY_PERIOD):
    dt_server_now = datetime.now(pytz.timezone(settings.SERVER_TZ))
    end = as_client_tz(dt_server_now)
    end = end.replace(hour=23, minute=59, second=59, microsecond=999999)

    if max_days is 'all':
        # VK was founded in 2006
        start = start.replace(year=2006, month=1, day=1)
    else:
        start = end - timedelta(days=max_days)
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    period = {
        'start': start,
        'end': end,
    }
    return period


def generate_summary_path(user_name, period):
    filename = "{0}. {1} - {2}.txt".format(
        user_name,
        period['start'].strftime(settings.DATETIME_FORMAT),
        period['end'].strftime(settings.DATETIME_FORMAT)
    )
    path = os.path.join(settings.SUMMARIES_PATH, filename)
    return path
