#Required modules
import urllib2 #retrieve the page
import codecs #to encode into utf-8 russian characters
import time #used for time.sleep()
import os #to check if a file exists
from bs4 import BeautifulSoup
from threading import Thread
import string
from datetime import datetime, timedelta
import unicodedata
from pprint import pprint
from logger import CreateLogFolders, WriteDataLog, WriteErrorLog, WriteDebugLog, ConsoleLog, Summarize
import smtplib#for mail sending

class VKStalk:
#Class description
# def __init__(self, user_id, debug_mode=False):
# def NormalizeUnicode(self, user_data):
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

    def __init__(self, user_id, debug_mode=False, email_notifications=False, email=''):
        self.user_id = user_id
        self.user_data = {}
        self.prev_user_data = {'online':'_not_found', 'status':'_not_found_first_start'}
        self.time_step = 15
        self.last_log = ''
        self.log = ''
        self.last_error = 'No errors yet =)'
        self.error_counter = 0
        self.logs_counter = 0
        self.version = "| VKStalk ver. 4.0.0 |"
        self.birth = datetime.now().strftime("%d-%B-%Y at %H:%M")
        self.data_logger_is_built = False
        self.error_logger_is_built = False
        self.debug_mode = debug_mode
        self.current_path = '/'.join(__file__.split('/')[:-1])
        self.filename = ''
        self.secondary_data_keys_list = []
        self.email_notifications = email_notifications
        self.mail_recipient = email
        self.mail_notification_hours = [10,23]
        self.last_mail_time = -1
        self.summary_notification_days = [6]
        self.summary_notification_hours = [10]
        self.last_summary_mail_day = -1
        self.max_files_for_summary = 8 #7 will consider Mon-Sun. 8 for Sun-Sun, so that data saved on sunday after 10AM is also considered


        #pretify program version output
        self.version = '\n' + '='*((42-len(self.version))/2) + self.version + '='*((42-len(self.version))/2) + '\n\n'
        #create necessary folders
        CreateLogFolders()
        if self.debug_mode:
            WriteDebugLog('Log folders created', is_setup=False, userid=self.user_id)
        self.ClearScreen()
        #Print greeting message
        ConsoleLog('VKStalk successfully launched! Have a tea and analyze the results ;)', False)

    def ClearScreen(self):
        #Clear screen
        os.system( [ 'clear', 'cls' ][ os.name == 'nt' ] )

    def NormalizeUnicode(self, user_data):
        # Normalize and encode to ascii_letters
        for key in user_data.keys():
            if type(user_data[key]) is unicode:
                user_data[key] = unicodedata.normalize('NFKC', user_data[key]).encode('ascii','ignore')

    def PrepareLog(self):
        if self.debug_mode:
            WriteDebugLog('Preparing log', userid=self.user_id)
        #Save prev. log file
        self.last_log = self.log
        #Assume log will be written
        self.logs_counter += 1
        #General info. Written once on file creation.
        self.general_info = 'Log file created on' + time.strftime(' %d-%B-%Y at %H:%M:%S')
        for key in self.user_data.keys():
            self.general_info += '\n'+key.replace('_', ' ').capitalize()+': '+unicode(self.user_data[key])
        self.general_info += '\n\n\n\n'

        if self.debug_mode:
            WriteDebugLog('General info set', userid=self.user_id)
        #Common log to file
        self.log = (
                    self.user_data['name'] + '  --  ' +
                    self.user_data['last_visit'] +
                    '\nStatus: ' + self.user_data['status'] + '\n\n'
                    )
        #Looking for changes in secondary data
        try:
            if self.logs_counter > 1:
                secondary_data_changes = 0
                for key in self.secondary_data_keys_list:
                    if key in self.user_data.keys() and key in self.prev_user_data.keys():
                        if self.user_data[key] != self.prev_user_data[key]:
                            secondary_data_changes += 1
                            self.log = self.log.rstrip()+'\n'+key.replace('_', ' ').capitalize()+': '+str(self.prev_user_data[key])+' => '+str(self.user_data[key])+'\n'
                self.log += '\n'
        except Exception as e:
            self.HandleError(
                        step='Adding extra info to log.',
                        exception_msg=e,
                        dump_vars=True,
                        console_msg='Error while adding extra info to the log.\n'+str(e)
                        )
            pass
        #Generating a timestamp and adding it to the log string
        self.log_time = datetime.strftime(datetime.now(),'>>>Date: %d-%m-%Y. Time: %H:%M:%S\n')
        self.log = self.log_time + self.log.rstrip() + '\n\n'

        #first log to file
        filename = time.strftime('%Y.%m.%d') + '-' + self.user_data['name'] + '.log'
        path = os.path.join(self.current_path, "Data","Logs",filename)
        first_log_to_file = not os.path.exists(path)
        self.filename = path

        if ((self.user_data['online']!=self.prev_user_data['online'])
        or (self.user_data['mobile_version']!=self.prev_user_data['mobile_version'])
        or (self.user_data['status']!=self.prev_user_data['status'])
        or (self.user_data['name']!=self.prev_user_data['name'])
        or (first_log_to_file)
        or (secondary_data_changes>0)):
            write_log = True # a log should be written. There is new data.
        else:
            #Assumption was wrong. The log wasn't written thus, counter decreased.
            self.logs_counter -= 1
            write_log = False # No need to write the log, there is no new data.

        #Prepare output to console
        self.console_log = (
                    self.version + 'Launched on ' + self.birth +
                    '\nUser ID: ' + self.user_id + '\nUser Name: ' + self.user_data['name']+
                    '\nLogs written: ' + str(self.logs_counter)+
                    '\nErrors occurred: ' + str(self.error_counter) +
                    '\n\n' + '='*14 + '| LATEST LOG |' + '='*14 + '\n\n' + self.log +
                    '='*14 + '| LAST ERROR |' + '='*14 + '\n\n' + self.last_error
                    )
        if first_log_to_file:#first log to file
            self.log = self.general_info + self.log

        if self.debug_mode:
            WriteDebugLog('Log preparation finished', userid=self.user_id)
        #Save previous data
        #update last user_data to the current one
        self.prev_user_data = self.user_data

        #Send email if the time has come =)
        try:
            current_step = 'Sending email.'
            if self.debug_mode:
                WriteDebugLog(current_step, userid=self.user_id)
            if (self.email_notifications
            and (datetime.now().hour in self.mail_notification_hours)
            and (datetime.now().hour != self.last_mail_time)):
                current_step = "Trying to send daily email."
                if self.debug_mode:
                    WriteDebugLog(current_step, userid=self.user_id)
                if self.SendMail():
                    self.last_mail_time = datetime.now().hour
        except Exception as e:
            current_step = "Could not send DAILY email."
            if self.debug_mode:
                WriteDebugLog(current_step, userid=self.user_id)
            self.HandleError(
                        step=current_step,
                        exception_msg=e,
                        dump_vars=True,
                        console_msg='Could not send email.\n'+str(e)
                        )
            pass

        #Send summary email if the time has come =)
        try:
            current_step = 'Preparing a summary.'
            if self.debug_mode:
                WriteDebugLog(current_step, userid=self.user_id)
            if (self.email_notifications
            and (datetime.now().hour in self.summary_notification_hours)
            and (time.localtime().tm_wday in self.summary_notification_days)
            and (datetime.now().day != self.last_summary_mail_day)):
                current_step = "Trying to send summary mail."
                if self.debug_mode:
                    WriteDebugLog(current_step, userid=self.user_id)
                if self.SendMail(mail_type='summary', filename=Summarize(user_name=self.user_data['name'], max_files=self.max_files_for_summary)):
                    self.last_summary_mail_day = datetime.now().day
        except Exception as e:
            current_step = "Could not send SUMMARY email."
            if self.debug_mode:
                WriteDebugLog(current_step, userid=self.user_id)
            self.HandleError(
                        step=current_step,
                        exception_msg=e,
                        dump_vars=True,
                        console_msg='Could not send summary email.\n'+str(e)
                        )
            pass

        self.ClearScreen()
        return write_log

    def CookSoup(self):
        # Return the soup obtained from scrapping the page or False if any
        # error occured while connecting

        # Target URLs for VK and Mobile VK
        self.raw_url = 'http://vk.com'
        self.url = self.raw_url + '/'
        # url_mobile='http://m.vk.com/'

        #generate user specific URLs
        if self.debug_mode:
            WriteDebugLog('Generating URLs', userid=self.user_id)

        if self.user_id.isdigit():
            self.url += 'id' + self.user_id
            # url_mobile += 'id' + self.user_id
        else:
            self.url +=  self.user_id
            # url_mobile += self.user_id

        #requesting the page
        if self.debug_mode:
            WriteDebugLog('Fetching HTML page', userid=self.user_id)
        
        try:
            cHandle = urllib2.urlopen(self.url, timeout=20)
            self.html = cHandle.read()
            cHandle.close()
        except Exception as e:
            self.HandleError(
                        step='Fetching HTML page.',
                        exception_msg=e,
                        dump_vars=True,
                        console_msg='Could not fetch HTML page. Retrying in 7 seconds...',
                        sleep=7,
                        debug_msg='Restarting request.'
                        )
            return False

        #set soup
        if self.debug_mode:
            WriteDebugLog('Cooking soup', userid=self.user_id)
        self.soup = BeautifulSoup(self.html)
        if self.debug_mode:
            WriteDebugLog('Cooking soup finished', userid=self.user_id)

        return True

    def GetUserData(self):
        # Returns a dictionary with user data
        # The following data is available depending on user-specific
        # security settings: name, photo, isOnline or last visited time, 
        # skype, instagram, facebook, phone_number, university, number
        # of photos, nr of posts on the wall, nr. of audio files, nr. of
        # online friends, some of the friends who are online, nr. of friends
        # nr. of gifts. Some more data is much less relevant.

        #Check if the profile is not hidden. Page was deleted or does not exit.
        max_retries = 10
        for retry_counter in range(max_retries):
            if self.debug_mode:
                WriteDebugLog('Checking if the profile exists and is accessible. Attempt ('+str(retry_counter+1)+' of '+str(max_retries)+')', userid=self.user_id)
            if ((self.soup.find('div',{'class':'service_msg_null'}))
            or ('This user deleted their page. Information unavailable.' in self.soup.text)
            or ('This page is either deleted or has not been created yet.' in self.soup.text)):
                self.ClearScreen()
                self.HandleError(
                    step='Verifying if profile is accessible. Attempt ('+str(retry_counter+1)+' of '+str(max_retries)+')',
                    exception_msg='Access forbidden. Profile PRIVATE or page does not exist.',
                    debug_msg='Access forbidden. Profile PRIVATE or page does not exist. Attempt ('+str(retry_counter+1)+' of '+str(max_retries)+')',
                    sleep=15,
                    console_msg=(
                        'Access forbidden. Profile PRIVATE or page does not exist.\nAttempt ('
                        +str(retry_counter+1)+' of '+str(max_retries)+').\nRetry in 15 seconds...\n'
                        )
                    )
                ConsoleLog('Fetching user data...')
                self.CookSoup()
                profile_private = True
            else:
                if self.debug_mode:
                    WriteDebugLog('Profile PUBLIC. OK!', userid=self.user_id)
                profile_private = False
                break
        if profile_private:
            self.SendMail(mail_type='error', msg="Execution terminated! Private profile. Access forbidden.")
            exit("Private profile. Access forbidden")

        
        if self.debug_mode:
            WriteDebugLog('Initializing user_data with default values', userid=self.user_id)
        # Initialize user_data dictionary with default values
        user_data = {}
        #Primary data
        user_data['name'] = '_not_found'
        user_data['status'] = '_not_found'
        user_data['online'] = '_not_found'
        user_data['last_visit'] = '_not_found'
        user_data['mobile_version'] = False
        #Secondary data
        user_data['skype'] = '_not_found'
        user_data['site'] = '_not_found'
        user_data['twitter'] = '_not_found'
        user_data['instagram'] = '_not_found'
        user_data['facebook'] = '_not_found'
        user_data['phone'] = '_not_found'
        user_data['university'] = '_not_found'
        user_data['photo'] = '_not_found'
        user_data['birthday'] = '_not_found'
        user_data['hometown'] = '_not_found'
        user_data['current_city'] = '_not_found'
        #other secondary data entries are added during runtime. These depend on the profile of the user.
        self.secondary_data_keys_list = []
        
        if self.debug_mode:
            WriteDebugLog('Done', userid=self.user_id)

        #:Data fetching
        if self.debug_mode:
            WriteDebugLog('Start data fetching', userid=self.user_id)
        ###:Name
        if self.debug_mode:
            WriteDebugLog('Obtaining username', userid=self.user_id)
        try:
            user_data['name']=self.soup.html.head.title.text
            self.NormalizeUnicode(user_data)
            valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)#for filename verification
        
            #Sanitize user name
            for c in user_data['name']:
                if c not in valid_chars:
                    user_data['name'] = user_data['name'].replace(c,'')
            if user_data['name'][-2:] == 'VK':
                user_data['name'] = user_data['name'][:-2].rstrip()
        except Exception as e:
            self.HandleError(step='Setting username.', exception_msg=e, dump_vars=True)
            return False

        ###:Status
        if self.debug_mode:
            WriteDebugLog('Obtaining user status', userid=self.user_id)
        status = self.soup.find('div', {"class":"status"})
        if status:
            user_data['status'] = status.text
        else:
            status = self.soup.find('div',{'class':'pp_status'})
            if status:
                user_data['status'] = status.text

        ###:Mobile version or not
        if self.debug_mode:
            WriteDebugLog('Determining if user is logged in from a mobile device.', userid=self.user_id)
        try:
          if self.soup.find(class_='mlvi') is not None: #alt: self.soup.find('b',{'class':'lvi mlvi'})
            user_data['mobile_version'] = True
        except Exception as e:
            self.HandleError(step='Determining if user is logged in from a mobile device.', exception_msg=e, dump_vars=True)
            return False

        ###:Online OR not [last seen time]
        if self.debug_mode:
            WriteDebugLog('Obtaining info about user ONLINE status (online/offline)', userid=self.user_id)
        try:
        #If no concrete message for user being offline. Thus, will assume
        #that if last seen time is not found, the user is Online
            last_seen = self.soup.find('div',{'class':'lv'})
            if last_seen:
                last_seen = last_seen.text
            else:
                last_seen = self.soup.find('div',{'class':'pp_last_activity'})
                if last_seen:
                    last_seen = last_seen.text
                else:
                    last_seen = self.soup.find('b',{'id':'profile_time_lv'})
                    if last_seen:
                        last_seen = last_seen.text

            if last_seen and last_seen!='':
                user_data['online'] = False
                date_found = False
                user_data['last_visit'] = last_seen
                last_seen = last_seen.replace('last seen ', '')
                
                if ('am' in last_seen) or ('pm' in last_seen):
                    # Set timedelta according to daylight savings time
                    if time.localtime().tm_isdst == 1:
                        hours_delta = 1
                        time_delta = timedelta(hours=hours_delta)
                    else:
                        hours_delta = 2
                        time_delta = timedelta(hours=hours_delta)

                    for c in last_seen[:last_seen.find('at')]:
                        if c.isdigit():
                            date_found = True
                            break
                    if date_found:
                        try:
                            date_time = datetime.strptime(last_seen, "%d %B at %I:%M %p")
                            #By default year is 1900 and if time 00.41, minus delta it gets year
                            #1899 and raises an error
                            date_time = date_time.replace(year=datetime.now().year)
                            date_time = date_time - time_delta
                            user_data['last_visit'] = date_time.strftime("last seen on %B %d at %H:%M")
                        except Exception as e:
                            self.HandleError(step="Parsing date/time in last_seen.", exception_msg=e, dump_vars=True)
                            return False
                    else:
                        try:
                            date_time = datetime.strptime(last_seen[last_seen.find('at'):], "at %I:%M %p")
                            #By default year is 1900 and if time 00.41, minus delta it gets year
                            #1899 and raises an error
                            date_time = date_time.replace(year=datetime.now().year)
                            date_time = date_time - time_delta
                            user_data['last_visit'] = 'last seen ' + date_time.strftime(last_seen[:last_seen.find('at')]+"at %H:%M")
                            if ('yesterday' in last_seen) and (datetime.now().hour-hours_delta < 0):
                                user_data['last_visit'] = user_data['last_visit'].replace('yesterday','today')
                            elif ('yesterday' in last_seen) and (datetime.now().hour-hours_delta >= 0) and (date_time.hour+hours_delta >= 24):
                                user_data['last_visit'] = user_data['last_visit'].replace('yesterday','two days ago')
                            elif ('today' in last_seen) and (date_time.hour+hours_delta >= 24):
                                user_data['last_visit'] = user_data['last_visit'].replace('today','yesterday')
                        except Exception as e:
                            self.HandleError(step="Parsing time in last_seen", exception_msg=e, dump_vars=True)
                            return False

                elif last_seen.lower()=='online':
                    user_data['online']=True
                    user_data['last_visit']='Online'
                    
                else:#print raw last_seen data
                    user_data['last_visit'] = 'last seen ' + last_seen#+' That is raw data!'
            else:
                user_data['online']=True
                user_data['last_visit']='Online'
            
            if user_data['mobile_version']:
                    user_data['last_visit'] += ' [Mobile]'

        except Exception as e:
            self.HandleError(step="Determining user's online status.", exception_msg=e, dump_vars=True)
            return False

        #Secondary data fectching
        try:
            current_step = "Fetching secondary data"
            secondary_data_names_list = ['Skype', 'Twitter', 'Instagram', 'University', 'Birthday', 'Facebook', 'Website', 'Phone', 'Hometown', 'Current city']
            self.short_profile_info = []

            current_step = "Parsing 'pinfo_row'"
            for item in self.soup.findAll(class_='pinfo_row'):
                text = item.text
                if ':' in text:
                    self.short_profile_info.append(text)

            current_step = "Saving parsed data to 'user_data'"
            for item in self.short_profile_info:
                for data_name in secondary_data_names_list:
                    if data_name in item:
                        user_data[data_name.lower()] = item.split(':')[-1]
                    self.secondary_data_keys_list.append(data_name.lower())

            current_step = "Getting extra data (e.g. number of photos/communities)"
            extra_data = self.soup.find(class_='profile_menu')
            if extra_data:
                extra_data_list = []
                extra_data = extra_data.findAll(class_='pm_item')
                for item in extra_data:
                    item = item.text.lower()
                    if 'show more' not in item:
                        extra_data_list.append(item)
            current_step = "Parsing extra data (e.g. number of photos/communities)"
            for item in extra_data_list:
                item_parts = item.split(' ')
                key = ''
                value = ''
                for part in item_parts:
                    if part.isdigit():
                        value = part
                    elif not part.isdigit():
                        key += part+'_'
                key = key.replace('_',' ').rstrip().replace(' ','_')
                self.secondary_data_keys_list.append(key)
                user_data[key] = value

            current_step = "Getting number of wall posts"
            all_slim_headers = self.soup.findAll(class_='slim_header')
            if len(all_slim_headers)>0:
                for item in all_slim_headers:
                    if 'post' in item.text:
                        number_of_wallposts = item.text.split()[0]
                        number_of_wallposts = number_of_wallposts.encode('ascii','ignore')
                        #clear number from punctuation
                        table = string.maketrans("","")
                        number_of_wallposts = number_of_wallposts.translate(table, string.punctuation)
                        if number_of_wallposts.isdigit():
                            user_data['number_of_wallposts'] = number_of_wallposts
                            self.secondary_data_keys_list.append('number_of_wallposts')
                        else:
                            break

            current_step = "Getting link to profile photo."
            short_profile = self.soup.find(id="mcont")
            if short_profile is not None:
                short_profile = short_profile.find(class_='owner_panel')
                if short_profile is not None:
                    photo_tag = short_profile.find('a')
                    if photo_tag is not None:
                        photo_link = photo_tag.get('href')
                        if photo_link is not None:
                            user_data['photo'] = self.raw_url+photo_link
                            self.secondary_data_keys_list.append('photo')

        except Exception as e:
            self.HandleError(step=current_step, exception_msg=e, dump_vars=True, debug_msg=current_step)
            return False
            
        #set object user_data
        self.user_data = user_data

        return True

    ######Logging part######
    def ShowWriteInfo(self):
        #if there's new user data,  a new status or online changed from False to True or True to False
        #write the new log to file
        filename = time.strftime('%Y.%m.%d') + '-' + self.user_data['name'] + '.log'
        path = os.path.join(self.current_path, "Data","Logs"+filename)
        write_log = self.PrepareLog()
        if write_log:
            if self.debug_mode:
                WriteDebugLog('Writing log to file', userid=self.user_id)
            try:
                self.data_logger_is_built = WriteDataLog(self.log, filename, self.data_logger_is_built and self.user_data['name'] in filename)
            except Exception as e:
                self.HandleError(
                        step='Writing Data log to file.',
                        exception_msg=e,
                        dump_vars=True,
                        console_msg='Could not write log. Retrying in 10 seconds...',
                        sleep=10,
                        debug_msg='Restarting request.'
                        )
                return False

        try:
            if self.debug_mode:
                WriteDebugLog('Output to console', userid=self.user_id)
            ConsoleLog(self.console_log)
        except Exception as e:
            self.HandleError(
                        step='Output log to console.',
                        exception_msg=e,
                        dump_vars=True,
                        console_msg='Could not write console log. Retrying in 10 seconds',
                        sleep=10,
                        debug_msg='Restarting request.'
                        )
            return False
        return True

    #######################################END logging#######################################

    #ERROR handler
    def HandleError(self, step='unspecified', exception_msg='unspecified', dump_vars=False, console_msg='', sleep='', debug_msg=''):
        self.error_counter += 1
        self.last_error = 'STEP: ' + step + '\nException: ' + str(exception_msg) + '\n'
        self.error_logger_is_built = WriteErrorLog(self.last_error, self.error_logger_is_built, userid=self.user_id)
        self.last_error =  datetime.strftime(datetime.now(),'[Date: %d-%m-%Y. Time: %H:%M:%S] - ') + self.last_error

        if dump_vars:
            #Dump vars
            try:
                filename = 'VAR_DUMP - ' + self.user_id + time.strftime(' - %Y.%m.%d') + '.txt'
                path = os.path.join(self.current_path, "Data", "Errors", filename)
                with open(path, 'wt') as out:
                    pprint(self.user_data, stream=out)
            except:
                self.error_logger_is_built = WriteErrorLog('Variable dump - FAILED', self.error_logger_is_built, userid=self.user_id)
        if console_msg:
            ConsoleLog(console_msg)
        if sleep:
            time.sleep(sleep)
        if debug_msg and self.debug_mode:
            WriteDebugLog(debug_msg, userid=self.user_id)

    ##Mail sending
    def SendMail(self, mail_type='daily', msg='default_message', filename=''):
        ConsoleLog('Sending '+mail_type+' email...')

        TEXT = ''
        SUBJECT = ''
        if mail_type == 'daily':
            # Add number of logs and error to message
            TEXT += 'Logs written: '+str(self.logs_counter)
            TEXT += '\nErrors occured: '+str(self.error_counter)
            TEXT += '\nLast error: '+str(self.last_error)+'\n\n\n'
            # Writing the message (this message will appear in the email)
            SUBJECT = 'VKStalk report. Name: '+self.user_data['name']+'. ID: '+self.user_id
            if self.filename:
                file_handle = open(self.filename,'r')
                TEXT = TEXT + file_handle.read()
                file_handle.close()
        elif mail_type == 'error':
            # Writing the message (this message will appear in the email)
            SUBJECT = 'VKStalk ERROR. User ID: '+self.user_id
            TEXT += msg
        elif mail_type == 'summary':
            # Writing the message (this message will appear in the email)
            SUBJECT = 'VKStalk summary. Name: '+self.user_data['name']+'. ID: '+self.user_id
            if self.filename:
                file_handle = open(filename,'r')
                TEXT = TEXT + file_handle.read()
                file_handle.close()

        #Constructing the message
        message = 'Subject: %s\n\n%s' % (SUBJECT, TEXT)    
        # Specifying the from and to addresses
        fromaddr = 'vkstalk@gmail.com'
        if not self.mail_recipient:
            ConsoleLog('Mail NOT sent!')
            self.ClearScreen()
            return False
        toaddrs  = self.mail_recipient
         
        
         
        # Gmail Login
         
        mail_username = 'stalkvk'
        mail_password = 'sG567.mV11'
         
        # Sending the mail  
         
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(mail_username,mail_password)
        server.sendmail(fromaddr, toaddrs, message)
        server.quit()
        ConsoleLog('Mail sent!')
        return True

    ##Summarizer
    #Send summaries by email, every Sunday at 9AM
    def Summarize(self):

        pass

    #########################################################################################

    def SingleRequest(self):
        ConsoleLog('Fetching user data...')
        if self.debug_mode:
            WriteDebugLog('Start single request', userid=self.user_id)
        if self.CookSoup() == False:
            return False
        if self.GetUserData() == False:
            return False
        
        self.ClearScreen()
        if not self.ShowWriteInfo():
            return False

        if self.debug_mode:
            WriteDebugLog('Finished single request\n\n', userid=self.user_id)

    def Work(self):
        if self.debug_mode:
            WriteDebugLog('Begin work', userid=self.user_id)
        while True:
            if self.SingleRequest() == False:
                break
            time.sleep(self.time_step)
        ##RESTART APP###
        self.ClearScreen()
        #Restart main cycle
        self.Work()