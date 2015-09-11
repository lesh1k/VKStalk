from __future__ import unicode_literals
import os
import unicodedata


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
