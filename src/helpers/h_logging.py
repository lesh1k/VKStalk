from config import settings
import logging
import logging.config
import os


def setup_logging(user_id=0):
    # Makes directories for all log types, according to config.py
    try:
        os.mkdir(settings.LOGS_PATH)
    except OSError as e:
        if e.errno != 17:  # (17, 'File exists')
            raise
        print "Path '{0}' already exists, nothing to do here".format(
            settings.LOGS_PATH)

    logging.config.dictConfig(settings.LOGGING)


def get_logger(logger_name, autoprefix=True):
    if autoprefix and settings and hasattr(settings, 'PROJECT_NAME'):
        logger_name = "{0}.{1}".format(settings.PROJECT_NAME, logger_name)
    return logging.getLogger(logger_name)
