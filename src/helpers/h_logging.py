from config import settings
import logging
import logging.config
import os


def setup_logging(user_id=0):
    try:
        os.mkdir(settings.LOGS_PATH)
    except OSError as e:
        if e.errno != 17:  # (17, 'File exists')
            raise

    logging.config.dictConfig(settings.LOGGING)


def get_logger(logger_name, autoprefix=True):
    if autoprefix and settings and hasattr(settings, 'PROJECT_NAME'):
        logger_name = "{0}.{1}".format(settings.PROJECT_NAME, logger_name)
        logger_name = logger_name.lower()
    return logging.getLogger(logger_name)
