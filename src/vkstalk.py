# -*- coding: utf-8 -*-

# Required modules
from __future__ import unicode_literals
import urllib2  # retrieve the page
import codecs  # to encode into utf-8 russian characters
import time  # used for time.sleep()
import os  # to check if a file exists
from bs4 import BeautifulSoup
# from threading import Thread
import string
from datetime import datetime, timedelta
from pprint import pprint
from logger import Logger, Summarize
import smtplib  # for mail sending
from user import User as UserObj
import config
import urlparse
import sys
from utils import clear_screen, normalize_unicode
from parser import Parser
from models import *


class VKStalk:
    # Class description
    # def __init__(self, user_id, debug_mode=False):
    # def normalize_unicode(self, user_data):
    #     transform all non standard utf8 text to ascii
    #
    # def PrepareLog(self):
    #     using fetched data prepares a log message to console
    #     and a log message that might be written to file. Sets
    #     self.console_log, self.last_log and self.log
    #
    # def CookSoup(self):
    #     makes BeautifulSoup from fetched HTML
    #
    # def GetUserData(self):
    #     parses the soup and gets all the required data
    #
    # def ShowWriteInfo(self):
    #     Outputs self.console_log to console
    #     and if necessary writes self.log to file
    #
    # def SingleRequest(self):
    #     one call that gives the result. It fetches, parses data.
    #     Then prepares output data and presents it.
    #
    # def Work(self):
    #     Starts an infinite loop (while True) calling self.SingleRequest()

    def __init__(self, user_id, log_level=21, email_notifications=False, email=''):
        self.birth = datetime.now().strftime(config.DATETIME_FORMAT)

        self.user = UserObj(user_id)
        self.prev_user = None

        self.vk_logger = Logger(user_id, 10)

        self.version = "| VKStalk ver. {} |".format(config.VERSION)
        # pretify program version output
        self.version = '\n' + '=' * \
            ((42 - len(self.version)) / 2) + self.version + \
            '=' * ((42 - len(self.version)) / 2) + '\n\n'

        self.mail_notification_hours = config.MAIL_NOTIFICATION_HOURS
        self.summary_notification_days = config.REPORT_DAYS
        self.summary_notification_hours = config.REPORT_HOURS
        self.max_files_for_summary = config.MAX_FILES_PER_REPORT

        self.prev_log = ''
        self.log = ''
        self.last_error = None
        self.error_counter = 0
        self.logs_counter = 0

        # self.data_logger_is_built = False
        # self.error_logger_is_built = False
        # self.debug_mode = debug_mode
        # self.current_path = '/'.join(__file__.split('/')[:-1])
        # self.filename = ''
        # self.secondary_data_keys_list = []
        self.email_notifications = email_notifications
        self.mail_recipient = email
        self.last_mail_time = -1
        self.last_summary_mail_day = -1
        # 7 will consider Mon-Sun. 8 for Sun-Sun, so that data saved on sunday
        # after 10AM is also considered

        self.prev_photo_change = None
        self.prev_photos_with_change = None

        clear_screen()
        # Print greeting message
        # self.vk_logger.console_log(
        #     "VKStalk successfully launched! Have a tea and analyze the results.")

    def PrepareLog(self):
        self.vk_logger.logger.debug('Preparing log')
        # Save prev. log file
        # self.last_log = self.log
        # Assume log will be written
        self.logs_counter += 1

        # Common log to file
        self.log = "{0} -- {1}\nStatus: {2}\n\n".format(self.user.name,
                                                        self.user.last_visit,
                                                        self.user.status
                                                        )
        # Looking for changes in secondary data
        # try:
        #     if self.logs_counter > 1:
        #         secondary_data_changes = 0
        #         for key in self.secondary_data_keys_list:
        # if key in self.user_data.keys() and key in
        # self.prev_user_data.keys():

        #                 if "photos" == key and self.user_data[key] != self.prev_user_data[key]:
        #                     if self.prev_photo_change and self.user_data[key] in self.prev_photo_change and self.prev_user_data[key] in self.prev_photo_change:
        #                         continue
        #                     else:
        #                         self.prev_photo_change = [
        # self.prev_user_data[key], self.user_data[key]]

        #                 if "photos_with_" in key and self.user_data[key] != self.prev_user_data[key]:
        #                     if self.prev_photos_with_change and self.user_data[key] in self.prev_photos_with_change and self.prev_user_data[key] in self.prev_photos_with_change:
        #                         continue
        #                     else:
        #                         self.prev_photos_with_change = [
        # self.prev_user_data[key], self.user_data[key]]

        #                 if self.user_data[key] != self.prev_user_data[key]:
        #                     secondary_data_changes += 1
        #                     self.log = self.log.rstrip() + '\n' + key.replace('_', ' ').capitalize() + \
        #                         ': ' + \
        #                         str(self.prev_user_data[
        #                             key]) + ' => ' + str(self.user_data[key]) + '\n'
        #         self.log += '\n'
        # except Exception as e:
        #     self.vk_logger.logger.error(
        #         "Error while adding extra info to the log: {}".format(e))
        # self.HandleError(
        #     step='Adding extra info to log.',
        #     exception_msg=e,
        #     dump_vars=True,
        #     console_msg='Error while adding extra info to the log.\n' +
        #     str(e)
        # )
        # pass
        # Generating a timestamp and adding it to the log string
        self.log_time = datetime.strftime(
            datetime.now(), '>>>Date: %d-%m-%Y. Time: %H:%M:%S\n')
        self.log = self.log_time + self.log.rstrip() + '\n\n'

        # first log to file
        # filename = time.strftime(
        #     '%Y.%m.%d') + '-' + self.user.name + '.log'
        # path = os.path.join(self.current_path, "Data", "Logs", filename)
        # first_log_to_file = not os.path.exists(path)
        # self.filename = path

        # if ((self.user_data['online'] != self.prev_user_data['online'])
        #         or (self.user_data['mobile_version'] != self.prev_user_data['mobile_version'])
        #         or (self.user_data['status'] != self.prev_user_data['status'])
        #         or (self.user.name != self.prev_user.name)
        #         or (first_log_to_file)
        #         or (secondary_data_changes > 0)):
        # write_log = True  # a log should be written. There is new data.
        # else:
        # Assumption was wrong. The log wasn't written thus, counter
        # decreased.
        #     self.logs_counter -= 1
        # No need to write the log, there is no new data.
        #     write_log = False

        # Prepare output to console
        self.console_log = config.CONSOLE_LOG_TEMPLATE.format(
            self.version,
            self.birth,
            self.user.id,
            self.user.name,
            self.logs_counter,
            self.error_counter,
            self.log,
            self.last_error,
        )

        self.vk_logger.log_activity("")  # triggers file creation if time has come
        log_file_size = os.stat(self.vk_logger.activity_log_file).st_size

        if log_file_size == 1:
            # first log to file. 1 byte size, because of logger adding \n
            file_handle = open(self.vk_logger.activity_log_file, 'w')
            file_handle.write("")
            file_handle.close()
            # General info. Written once, on file creation.
            self.general_info = "Log file created on {}".format(
                time.strftime('%d-%B-%Y at %H:%M:%S'))
            for attr, value in self.user.__dict__.iteritems():
                self.general_info += "\n{0}: {1}".format(
                    attr.replace('_', ' ').capitalize(),
                    value
                    )
            self.general_info += '\n\n\n\n'

            self.vk_logger.logger.debug('General info set')
            self.log = self.general_info + self.log

        self.vk_logger.logger.debug('Log preparation finished')
        # Save previous data
        # update last user_data to the current one
        self.prev_user = self.user

        # Send email if the time has come =)
        # try:
        #     current_step = 'Sending email.'
        #     if self.debug_mode:
        #         WriteDebugLog(current_step, userid=self.user_id)
        #     if (self.email_notifications
        #             and (datetime.now().hour in self.mail_notification_hours)
        #             and (datetime.now().hour != self.last_mail_time)):
        #         current_step = "Trying to send daily email."
        #         if self.debug_mode:
        #             WriteDebugLog(current_step, userid=self.user_id)
        #         if self.SendMail():
        #             self.last_mail_time = datetime.now().hour
        # except Exception as e:
        #     current_step = "Could not send DAILY email."
        #     if self.debug_mode:
        #         WriteDebugLog(current_step, userid=self.user_id)
        #     self.HandleError(
        #         step=current_step,
        #         exception_msg=e,
        #         dump_vars=True,
        #         console_msg='Could not send email.\n' + str(e)
        #     )
        #     pass

        # Send summary email if the time has come =)
        # try:
        #     current_step = 'Preparing a summary.'
        #     if self.debug_mode:
        #         WriteDebugLog(current_step, userid=self.user_id)
        #     if (self.email_notifications
        #             and (datetime.now().hour in self.summary_notification_hours)
        #             and (time.localtime().tm_wday in self.summary_notification_days)
        #             and (datetime.now().day != self.last_summary_mail_day)):
        #         current_step = "Trying to send summary mail."
        #         if self.debug_mode:
        #             WriteDebugLog(current_step, userid=self.user_id)
        #         if self.SendMail(mail_type='summary', filename=Summarize(user_name=self.user_data['name'], max_files=self.max_files_for_summary)):
        #             self.last_summary_mail_day = datetime.now().day
        # except Exception as e:
        #     current_step = "Could not send SUMMARY email."
        #     if self.debug_mode:
        #         WriteDebugLog(current_step, userid=self.user_id)
        #     self.HandleError(
        #         step=current_step,
        #         exception_msg=e,
        #         dump_vars=True,
        #         console_msg='Could not send summary email.\n' + str(e)
        #     )
        #     pass

        clear_screen()
        # return write_log
        return True

    def populate_user(self):
        p = Parser(self.user.url)
        user_data = p.get_user_data()
        self.save_data_to_db(user_data)

        for key in user_data.keys():
            setattr(self.user, key, user_data[key])

    def save_data_to_db(self, user_data):
        session = Session()

        user = session.query(User).filter_by(vk_id=self.user.id).first()
        if not user:
            user = User(vk_id=self.user.id)
            session.add(user)

        if not user.data:
            user.data = UserData()
        # import ipdb; ipdb.set_trace()
        try:
            keys = [i for i in user_data.keys() if i in user.data.__dict__.keys()]
            for key in keys:
                setattr(user.data, key, user_data[key])
        except:
            print "Error in '{}'".format(sys._getframe().f_code.co_name)
            print "Error setting key:value - {0}:{1}".format(key. user_data[key])
            session.rollback()
        finally:
            session.commit()
            session.close()

    ######Logging part######
    def ShowWriteInfo(self):
        # if there's new user data,  a new status or online changed from False to True or True to False
        # write the new log to file
        # filename = time.strftime(
        #     '%Y.%m.%d') + '-' + self.user_data['name'] + '.log'
        # path = os.path.join(self.current_path, "Data", "Logs" + filename)
        # write_log = self.PrepareLog()
        if self.PrepareLog():
            self.vk_logger.logger.debug('Writing log to file')
            try:
                self.vk_logger.log_activity(self.log)
                self.vk_logger.console_log(self.console_log)
            except Exception as e:
                self.vk_logger.logger.error(
                    "Error in writing Data to log file and console")
                # self.HandleError(
                #     step='Writing Data log to file.',
                #     exception_msg=e,
                #     dump_vars=True,
                #     console_msg='Could not write log. Retrying in 10 seconds...',
                #     sleep=10,
                #     debug_msg='Restarting request.'
                # )
                return False

        # try:
        #     self.vk_logger.logger.debug('Output to console')
        # ConsoleLog(self.console_log)
        # except Exception as e:
        # self.HandleError(
        # step='Output log to console.',
        # exception_msg=e,
        # dump_vars=True,
        # console_msg='Could not write console log. Retrying in 10 seconds',
        # sleep=10,
        # debug_msg='Restarting request.'
        # )
        #     return False
        return True

    #######################################END logging########################

    # ERROR handler
    def HandleError(self, step='unspecified', exception_msg='unspecified', dump_vars=False, console_msg='', sleep='', debug_msg=''):
        self.error_counter += 1
        self.vk_logger.logger.error(
            "Got to HandleError function, which is dummy!")
        pass
        # self.last_error = 'STEP: ' + step + \
        #     '\nException: ' + str(exception_msg) + '\n'
        # self.error_logger_is_built = WriteErrorLog(
        #     self.last_error, self.error_logger_is_built, userid=self.user_id)
        # self.last_error = datetime.strftime(
        # datetime.now(), '[Date: %d-%m-%Y. Time: %H:%M:%S] - ') +
        # self.last_error

        # if dump_vars:
        # Dump vars
        #     try:
        #         filename = 'VAR_DUMP - ' + self.user_id + \
        #             time.strftime(' - %Y.%m.%d') + '.txt'
        #         path = os.path.join(
        #             self.current_path, "Data", "Errors", filename)
        #         with open(path, 'wt') as out:
        #             pprint(self.user_data, stream=out)
        #     except:
        #         self.error_logger_is_built = WriteErrorLog(
        #             'Variable dump - FAILED', self.error_logger_is_built, userid=self.user_id)
        # if console_msg:
        #     ConsoleLog(console_msg)
        # if sleep:
        #     time.sleep(sleep)
        # if debug_msg and self.debug_mode:
        #     WriteDebugLog(debug_msg, userid=self.user_id)

    # Mail sending
    def SendMail(self, mail_type='daily', msg='default_message', filename=''):
        # ConsoleLog('Sending ' + mail_type + ' email...')

        TEXT = ''
        SUBJECT = ''
        if mail_type == 'daily':
            # Add number of logs and error to message
            TEXT += 'Logs written: ' + str(self.logs_counter)
            TEXT += '\nErrors occured: ' + str(self.error_counter)
            TEXT += '\nLast error: ' + str(self.last_error) + '\n\n\n'
            # Writing the message (this message will appear in the email)
            SUBJECT = 'VKStalk report. Name: ' + \
                self.user_data['name'] + '. ID: ' + self.user_id
            if self.filename:
                file_handle = open(self.filename, 'r')
                TEXT = TEXT + file_handle.read()
                file_handle.close()
        elif mail_type == 'error':
            # Writing the message (this message will appear in the email)
            SUBJECT = 'VKStalk ERROR. User ID: ' + self.user_id
            TEXT += msg
        elif mail_type == 'summary':
            # Writing the message (this message will appear in the email)
            SUBJECT = 'VKStalk summary. Name: ' + \
                self.user_data['name'] + '. ID: ' + self.user_id
            if self.filename:
                file_handle = open(filename, 'r')
                TEXT = TEXT + file_handle.read()
                file_handle.close()

        # Constructing the message
        message = 'Subject: %s\n\n%s' % (SUBJECT, TEXT)
        # Specifying the from and to addresses
        fromaddr = 'vkstalk@gmail.com'
        if not self.mail_recipient:
            # ConsoleLog('Mail NOT sent!')
            clear_screen()
            return False
        toaddrs = self.mail_recipient

        # Gmail Login

        mail_username = 'stalkvk'
        mail_password = 'sG567.mV11'

        # Sending the mail

        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(mail_username, mail_password)
        server.sendmail(fromaddr, toaddrs, message)
        server.quit()
        # ConsoleLog('Mail sent!')
        return True

    # Summarizer
    # Send summaries by email, every Sunday at 9AM
    def Summarize(self):

        pass

    ##########################################################################

    def SingleRequest(self):
        # ConsoleLog('Fetching user data...')
        self.vk_logger.logger.debug('Start single request')
        self.populate_user()

        clear_screen()
        if not self.ShowWriteInfo():
            return False

        self.vk_logger.logger.debug('Finished single request\n\n')

    def Work(self):
        # import ipdb; ipdb.set_trace()
        self.vk_logger.logger.debug('Begin work')
        while True:
            if self.SingleRequest() == False:
                break
            time.sleep(config.DATA_FETCH_INTERVAL)
        ##RESTART APP###
        clear_screen()
        # Restart main cycle
        self.Work()
