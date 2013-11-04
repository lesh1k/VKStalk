#ptyhon modules
import logging
import time #used for time.sleep()
import os #to check if a file exists

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
    #Creates the following tree if not present yet:
    #Data-> [Logs, Errors, Debug]
    current_path = '/'.join(__file__.split('/')[:-1])
    data_folder = os.path.join(current_path, "Data")
    error_folder = os.path.join(current_path, "Data", "Errors")
    logs_folder = os.path.join(current_path, "Data", "Logs")
    debug_folder = os.path.join(current_path, "Data", "Debug")

    try:
        if not os.path.exists(data_folder):
            os.mkdir(data_folder)
        if not os.path.exists(logs_folder):
            os.mkdir(logs_folder)
        if not os.path.exists(error_folder):
            os.mkdir(error_folder)
        if not os.path.exists(debug_folder):
            os.mkdir(debug_folder)
    except:
        #Here be the Error logging line#
        return False

def SetupLogging():
    CreateLogFolders()


def WriteDataLog(message, filename='', is_setup=False):
    #Writes the log to the respective file. Creates the file if 
    #necessary
    current_path = '/'.join(__file__.split('/')[:-1])
    path = os.path.join(current_path, "Data", "Logs", filename)
    if not is_setup or not os.path.exists(path):
        logger = logging.getLogger('data_logger')
        logger.handlers = []
        #setup logger
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

def WriteErrorLog(message, is_setup=True):
    #Writes the error log to the respective file

    current_path = '/'.join(__file__.split('/')[:-1])
    filename = 'ERRORS -' + time.strftime('%Y.%m.%d') + '.log'
    path = os.path.join(current_path, "Data", "Errors", filename)
    if not is_setup or not os.path.exists(path):
        logger = logging.getLogger('error_logger')
        logger.handlers = []
        #setup logger
        SetupLogger('error_logger', path, '%(levelname)s :: %(asctime)s :: %(message)s', '[Date: %d-%m-%Y. Time: %H:%M:%S]',
                    'a', logging.ERROR, add_stream_handler=False, add_file_handler=True)

    logger = logging.getLogger('error_logger')
    
    try:
        logger.error(message)
    except:
        #Here be the Error logging line#
        return False
    
    return True


def WriteDebugLog(message, is_setup=True):
    #Writes the debug log to the respective file
    
    current_path = '/'.join(__file__.split('/')[:-1])
    filename = 'DEBUG -' + time.strftime('%Y.%m.%d') + '.log'
    path = os.path.join(current_path, "Data", "Debug", filename)
    if not is_setup or not os.path.exists(path):
        logger = logging.getLogger('debug_logger')
        logger.handlers = []
        #setup logger
        SetupLogger('debug_logger', path, '%(levelname)s :: %(asctime)s :: %(message)s', '[Date: %d-%m-%Y. Time: %H:%M:%S]',
                    'a', logging.DEBUG, add_stream_handler=False, add_file_handler=True)

    logger = logging.getLogger('debug_logger')
    
    try:
        logger.debug(message)
    except:
        #Here be the Error logging line#
        return False
    
    return True

def ConsoleLog(message, is_setup=True):
    #Outputs info to console
    if not is_setup:
        #setup logger
        SetupLogger('console_logger', log_format='%(message)s',
                    level=logging.INFO, add_stream_handler=True, add_file_handler=False)
    logger = logging.getLogger('console_logger')
    try:
        logger.info(message)
    except:
        #Here be the Error logging line#
        return False
    
    return True