from __future__ import unicode_literals
import os
import unicodedata
import re
import string
from config import settings


def clear_screen():
    # Clear screen
    os.system(['clear', 'cls'][os.name == 'nt'])


def normalize_unicode(user):
    # Normalize and encode to ascii_letters
    for attr, val in user.__dict__.iteritems():
        if type(val) is unicode:
            setattr(
                user,
                attr,
                unicodedata.normalize(
                    'NFKC', val).encode('ascii', 'ignore')
            )


def print_obj(obj):
    for attr, val in obj.__dict__.iteritems():
        print "{0}: {1}".format(attr, val)


def convert_to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def get_all_digits_from_str(text):
    return ''.join([c for c in text if c.isdigit()])
