# ptyhon modules
import logging
import time  # used for time.sleep()
import os  # to check if a file exists
import string
import glob
import codecs


def SetupLogger(logger_name, log_file='empty.log', log_format=None, log_date_format=None,
                log_file_mode='a', level=logging.INFO,
                add_stream_handler=False, add_file_handler=False):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter(log_format, log_date_format)
    if add_file_handler:
        fileHandler = logging.FileHandler(log_file, mode=log_file_mode)
        fileHandler.setFormatter(formatter)
    if add_stream_handler:
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(formatter)

    l.setLevel(level)
    if add_file_handler:
        l.addHandler(fileHandler)
    if add_stream_handler:
        l.addHandler(streamHandler)


def CreateLogFolders():
    # Creates the following tree if not present yet:
    # Data-> [Logs, Errors, Debug]
    current_path = '/'.join(__file__.split('/')[:-1])
    data_folder = os.path.join(current_path, "Data")
    error_folder = os.path.join(current_path, "Data", "Errors")
    logs_folder = os.path.join(current_path, "Data", "Logs")
    debug_folder = os.path.join(current_path, "Data", "Debug")
    summaries_folder = os.path.join(current_path, "Data", "Summaries")

    try:
        if not os.path.exists(data_folder):
            os.mkdir(data_folder)
        if not os.path.exists(logs_folder):
            os.mkdir(logs_folder)
        if not os.path.exists(error_folder):
            os.mkdir(error_folder)
        if not os.path.exists(debug_folder):
            os.mkdir(debug_folder)
        if not os.path.exists(summaries_folder):
            os.mkdir(summaries_folder)
    except:
        #Here be the Error logging line#
        return False


def SetupLogging():
    CreateLogFolders()


def WriteDataLog(message, filename='', is_setup=False):
    # Writes the log to the respective file. Creates the file if
    # necessary
    current_path = '/'.join(__file__.split('/')[:-1])
    path = os.path.join(current_path, "Data", "Logs", filename)
    if not is_setup or not os.path.exists(path):
        logger = logging.getLogger('data_logger')
        logger.handlers = []
        # setup logger
        SetupLogger(
            'data_logger', path, log_format='%(message)s',
            log_file_mode='a', level=logging.INFO, add_stream_handler=False, add_file_handler=True
        )
    logger = logging.getLogger('data_logger')
    try:
        logger.info(message)
    except:
        #Here be the Error logging line#
        return False

    return True


def WriteErrorLog(message, is_setup=True, userid=''):
    # Writes the error log to the respective file

    current_path = '/'.join(__file__.split('/')[:-1])
    filename = 'ERRORS - ' + userid + time.strftime(' - %Y.%m.%d') + '.log'
    path = os.path.join(current_path, "Data", "Errors", filename)
    if not is_setup or not os.path.exists(path):
        logger = logging.getLogger('error_logger')
        logger.handlers = []
        # setup logger
        SetupLogger(
            'error_logger', path, log_format='%(levelname)s :: %(asctime)s :: %(message)s',
            log_date_format='[Date: %d-%m-%Y. Time: %H:%M:%S]', log_file_mode='a', level=logging.ERROR,
            add_stream_handler=False, add_file_handler=True
        )

    logger = logging.getLogger('error_logger')

    try:
        logger.error(message)
    except:
        #Here be the Error logging line#
        return False

    return True


def WriteDebugLog(message, is_setup=True, userid=''):
    # Writes the debug log to the respective file

    current_path = '/'.join(__file__.split('/')[:-1])
    filename = 'DEBUG - ' + userid + time.strftime(' - %Y.%m.%d') + '.log'
    path = os.path.join(current_path, "Data", "Debug", filename)
    if not is_setup or not os.path.exists(path):
        logger = logging.getLogger('debug_logger')
        logger.handlers = []
        # setup logger
        SetupLogger(
            'debug_logger', path, log_format='%(levelname)s :: %(asctime)s :: %(message)s',
            log_date_format='[Date: %d-%m-%Y. Time: %H:%M:%S]', log_file_mode='a',
            level=logging.DEBUG, add_stream_handler=False, add_file_handler=True
        )

    logger = logging.getLogger('debug_logger')

    try:
        logger.debug(message)
    except:
        #Here be the Error logging line#
        return False

    return True


def ConsoleLog(message, is_setup=True):
    # Outputs info to console
    if not is_setup:
        # setup logger
        SetupLogger(
            'console_logger', log_format='%(message)s',
            level=logging.INFO, add_stream_handler=True, add_file_handler=False
        )
    logger = logging.getLogger('console_logger')
    try:
        logger.info(message)
    except:
        #Here be the Error logging line#
        return False

    return True


def Summarize(user_name='', log_folder='Data/Logs/', extension=".log", max_files=-1):
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
