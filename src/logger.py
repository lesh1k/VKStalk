import config

# ptyhon modules
import logging
import logging.handlers
import time  # used for time.sleep()
import os  # to check if a file exists
import string
import glob
import codecs


class UserActivityTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    # filters out only logs with level == 21.
    # Meaning these are USER_ACTIVITY logs

    def emit(self, record):
        if not record.levelno == 21:
            return
        super(UserActivityTimedRotatingFileHandler, self).emit(record)


class UserActivityStreamHandler(logging.StreamHandler):
    # filters out only logs with level == 21.
    # Meaning these are USER_ACTIVITY logs

    def emit(self, record):
        if not record.levelno == 21:
            return
        logging.StreamHandler.emit(self, record)


class Logger:

    def __init__(self, user_id, log_level=logging.WARNING):
        self.user_id = user_id
        self.make_log_dirs()
        self.name = "logger_{}".format(user_id)
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        USER_ACTIVITY = 21
        logging.addLevelName(USER_ACTIVITY, "USER_ACTIVITY")

        console_handler = UserActivityStreamHandler()
        console_formatter = logging.Formatter("%(message)s")
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(USER_ACTIVITY)

        activity_log_file = os.path.join(
            config.USER_ACTIVITY_LOGS_PATH.format(self.user_id), self.user_id)
        activity_handler = UserActivityTimedRotatingFileHandler(
            activity_log_file, when="midnight")
        activity_formatter = logging.Formatter("%(message)s")
        activity_handler.setFormatter(activity_formatter)
        activity_handler.setLevel(USER_ACTIVITY)

        debug_log_file = os.path.join(
            config.LOGS_PATH.format(self.user_id), self.user_id)
        debug_handler = logging.handlers.TimedRotatingFileHandler(
            debug_log_file, when="midnight")
        debug_formatter = logging.Formatter(
            "%(levelname)s :: %(asctime)s :: %(message)s",
            "[Date: %d-%m-%Y. Time: %H:%M:%S]")
        debug_handler.setFormatter(debug_formatter)
        debug_handler.setLevel(log_level)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(activity_handler)
        self.logger.addHandler(debug_handler)

    def make_log_dirs(self):
        # Makes directories for all log types, according to config.py
        try:
            for path in config.LOGS_DIRECTORIES:
                os.mkdir(path.format(self.user_id))
        except OSError as e:
            if e.errno != 17:  # (17, 'File exists')
                raise
            print "Path '{0}' already exists, nothing to do here".format(
                path.format(self.user_id))

    def log_activity(self, message):
        self.logger.log(21, message)


def Summarize(user_name='', log_folder='Data/Logs/', extension=".log",
              max_files=-1):
    if not user_name:
        return False

    # save current working directory, so that we return here later
    initial_dir = '/'.join(__file__.split('/')[:-1])
    # get to logs folder
    log_folder = os.path.join(initial_dir, log_folder)
    os.chdir(log_folder)
    # get all log files list
    user_last_name = user_name.split()[-1]
    FILE_LIST = glob.glob('*' + user_last_name + extension)
    FILE_LIST.sort()
    # shorten list
    if max_files != -1 and len(FILE_LIST) > max_files:
        FILE_LIST = FILE_LIST[-max_files:]
    ALL_STATUSES = []
    UNIQUE_STATUSES = []
    UGLY_RESULT = []
    RESULT = {}
    DATA = {}
    # get the list of statuses per file. [decoded]
    for fileName in FILE_LIST:
        fHandle = open(fileName, 'r')
        fData = fHandle.readlines()
        fHandle.close()
        statusesList = []

        for line in fData:
            if 'Status:' in line:
                decodedString = codecs.decode(
                    line.replace('Status: ', ''), 'utf8')
                decodedString = decodedString.rstrip()
                statusesList.append(decodedString)
                ALL_STATUSES.append(decodedString)

        DATA[fileName.split('-I')[0]] = statusesList

    # Create the list of unique statuses
    UNIQUE_STATUSES = list(set(ALL_STATUSES))

    # Generate the list of tuples (nr_repetitions, status)
    for status in UNIQUE_STATUSES:
        UGLY_RESULT.append((ALL_STATUSES.count(status), status))

    # Sort the result descendingly depending on nr. of occurences
    UGLY_RESULT.sort()
    UGLY_RESULT.reverse()

    # Create a beautiful result
    for i in range(len(UGLY_RESULT)):
        RESULT[i + 1] = UGLY_RESULT[i]

    # get to initial folder
    os.chdir(initial_dir)
    # write result to file
    filename = 'SUMMARY - ' + user_name + time.strftime(' - %Y.%m.%d') + '.log'
    path = os.path.join(initial_dir, "Data", "Summaries")
    if not os.path.exists(path):
        return False
    path = os.path.join(initial_dir, "Data", "Summaries", filename)
    fHandle = open(path, 'w')
    for key in RESULT.keys():
        fHandle.write("%6d. %s \t  [x%d]\n" % (
            key, codecs.encode(string.ljust(RESULT[key][1], 150), 'utf8'), RESULT[key][0]))
    fHandle.close()

    return path
