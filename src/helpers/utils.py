from __future__ import unicode_literals
from config import settings

import os
import re
import string
import pytz


def clear_screen():
    # Clear screen
    os.system(['clear', 'cls'][os.name == 'nt'])


def print_obj(obj):
    for attr, val in obj.__dict__.iteritems():
        print "{0}: {1}".format(attr, val)


def convert_to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def parse_int(text):
    digits = ''.join([c for c in text if c.isdigit()])
    if digits.isdigit():
        return int(digits)
    return None


def as_client_tz(dt):
    return dt.astimezone(pytz.timezone(settings.CLIENT_TZ))


def make_data_updates_string(data_changes):
    updates = ""

    if data_changes:
        for key in data_changes:
            title = key.replace("_", " ").capitalize()
            old_val = data_changes[key]['old']
            new_val = data_changes[key]['new']
            updates += "\n{0}: {1} => {2}".format(title, old_val, new_val)

    return updates


def delta_minutes(now, before):
    delta_datetime = now - before
    minutes_ago = int(delta_datetime.total_seconds() / 60)
    return minutes_ago
