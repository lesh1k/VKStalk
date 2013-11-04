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
from logger import CreateLogFolders, WriteDataLog, WriteErrorLog, WriteDebugLog, ConsoleLog


class VKStalk:
#Class description

    def __init__(self, user_id, debug_mode=False):
        self.user_id = user_id
        self.user_data = {}
        self.prev_user_data = {'online':'_not_found', 'status':'_not_found'}
        self.time_step = 15
        self.last_log = ''
        self.log = ''
        self.last_error = 'No errors yet =)'
        self.error_counter = 0
        self.logs_counter = 0
        self.version = "| VKStalk ver. 4.0.0 BETA 2|"
        self.version = '\n' + '='*((42-len(self.version))/2) + self.version + '='*((42-len(self.version))/2) + '\n\n'
        self.birth = datetime.now().strftime("%d-%B-%Y at %H:%M")
        self.data_logger_is_built = False
        self.error_logger_is_built = False
        self.debug_mode = debug_mode

        CreateLogFolders()
        if self.debug_mode:
            WriteDebugLog('Log folders created', False)

        #Clear screen
        os.system( [ 'clear', 'cls' ][ os.name == 'nt' ] )
        #Print greeting message
        ConsoleLog('VKStalk successfully launched! Have a tea and analyze the results ;)', False)

    def NormalizeUnicode(self, user_data):
        # Normalize and encode to ascii_letters
        for key in user_data.keys():
            if type(user_data[key]) is unicode:
                user_data[key] = unicodedata.normalize('NFKD', user_data[key]).encode('ascii','ignore')

    def PrepareLog(self):
        if self.debug_mode:
            WriteDebugLog('Start preparing log')
        #Save prev. log file
        self.last_log = self.log

        self.general_info = ('Log file created on' + time.strftime(' %d-%B-%Y at %H:%M:%S') +
                        '\nUsername: '+self.user_data['name'] +
                        '\nStatus: ' + self.user_data['status'] + 
                        '\nBirthday: ' + self.user_data['birthday'] + 
                        '\nSkype: ' + self.user_data['skype'] + 
                        '\nSite: ' + self.user_data['site'] + 
                        '\nLast visit: ' + self.user_data['last_visit'] + 
                        '\nTwitter: ' + self.user_data['twitter'] + 
                        '\nInstagram: ' + self.user_data['instagram'] + 
                        '\nFacebook: ' + self.user_data['facebook'] + 
                        '\nPhone: ' + self.user_data['phone'] +
                        '\nUniversity: ' + self.user_data['university'] +
                        '\nPhoto: ' + self.user_data['photo'] +
                        '\nNumber of photos: ' + self.user_data['number_of_photos'] +
                        '\nNumber of posts: ' + self.user_data['number_of_posts'] +
                        '\nNumber of gifts: ' + self.user_data['number_of_gifts'] +
                        '\nNumber of friends: ' + self.user_data['number_of_friends'] +
                        '\n\n\n\n'
                        )
        if self.debug_mode:
            WriteDebugLog('Set general info')

        #Common log to file
        self.log = (
                    self.user_data['name'] + '  --  ' +
                    self.user_data['last_visit'] +
                    '\nStatus: ' + self.user_data['status'] + '\n\n'
                    )

        #Generating a timestamp and adding it to the log string
        self.log_time = datetime.strftime(datetime.now(),'>>>Date: %d-%m-%Y. Time: %H:%M:%S\n')
        self.log = self.log_time + self.log

        #prepare output to console
        self.console_log = (
                    self.version + 'Launched on ' + self.birth +
                    '\nUser ID: ' + self.user_id + '\nUser Name: ' + self.user_data['name']+
                    '\nLogs written: ' + str(self.logs_counter)+
                    '\nErrors occurred: ' + str(self.error_counter) +
                    '\n\n' + '='*14 + '| LATEST LOG |' + '='*14 + '\n\n' + self.log +
                    '='*14 + '| LAST ERROR |' + '='*14 + '\n\n' + self.last_error
                    )

        #first log to file
        current_path = '/'.join(__file__.split('/')[:-1])
        filename = time.strftime('%Y.%m.%d') + '-' + self.user_data['name'] + '.log'
        path = os.path.join(current_path, "Data/Logs/"+filename)

        if not os.path.exists(path):#first log to file
            self.log = self.general_info + self.log

        if self.debug_mode:
            WriteDebugLog('Set log')

        if self.debug_mode:
            WriteDebugLog('Set console log')
            WriteDebugLog('Log preparing finished')

    def CookSoup(self):
        # Return the soup obtained from scrapping the page or False if any
        # error occured while connecting

        # Target URLs for VK and Mobile VK
        url='http://vk.com/'
        url_mobile='http://m.vk.com/'

        #generate user specific URLs
        if self.debug_mode:
            WriteDebugLog('Generating URLs')

        if self.user_id.isdigit():
            url += 'id' + self.user_id
            url_mobile += 'id' + self.user_id
        else:
            url +=  self.user_id
            url_mobile += self.user_id

        #requesting the page
        if self.debug_mode:
            WriteDebugLog('Fetching HTML page')
        
        try:
            cHandle = urllib2.urlopen(url)
            self.html = cHandle.read()
            cHandle.close()
        except:
            self.error_counter += 1
            self.last_error = 'Could not fetch HTML page'
            self.error_logger_is_built = WriteErrorLog(self.last_error, self.error_logger_is_built)
            return False

        #set soup
        if self.debug_mode:
            WriteDebugLog('Cooking soup')
        self.soup = BeautifulSoup(self.html)
        if self.debug_mode:
            WriteDebugLog('Cooking soup finished')

    def GetUserData(self):
        # Returns a dictionary with user data
        # The following data is available depending on user-specific
        # security settings: name, photo, isOnline or last visited time, 
        # skype, instagram, facebook, phone_number, university, number
        # of photos, nr of posts on the wall, nr. of audio files, nr. of
        # online friends, some of the friends who are online, nr. of friends
        # nr. of gifts. Some more data is much less relevant.
        
        if self.debug_mode:
            WriteDebugLog('Initializing user_data with default values')
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
        user_data['number_of_photos'] = '_not_found'
        user_data['number_of_posts'] = '_not_found'
        user_data['number_of_gifts'] = '_not_found'
        user_data['number_of_friends'] = '_not_found'
        if self.debug_mode:
            WriteDebugLog('Done')

        #:Data fetching
        if self.debug_mode:
            WriteDebugLog('Start data fetching')
        ###:Name
        if self.debug_mode:
            WriteDebugLog('Obtaining username')
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
        except:
            self.error_counter += 1
            self.last_error = 'Could not set username'
            self.error_logger_is_built = WriteErrorLog(self.last_error, self.error_logger_is_built)
            return False

        ###:Status
        if self.debug_mode:
            WriteDebugLog('Obtaining user status')
        status = self.soup.find('div', {"class":"status"})
        if status:
            user_data['status'] = status.text
        else:
            status = self.soup.find('div',{'class':'pp_status'})
            if status:
                user_data['status'] = status.text

        ###:Mobile version or not
        # if self.debug_mode:
        #     WriteDebugLog('Determining if user is using mobile VK')
        # try:
        #   if self.soup.find('b',{'class':'lvi mlvi'}) != None:
        #       user_data['mobile_version'] = True
        # except:
        #   #Here be the Error logging line#
        #   # return False
        #   pass

        ###:Online OR not [last seen time]
        if self.debug_mode:
            WriteDebugLog('Obtaining info about user ONLINE status (online/offline)')
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
                        except:
                            self.error_counter += 1
                            self.last_error = 'Error while parsing date/time in last_seen'
                            self.error_logger_is_built = WriteErrorLog(self.last_error, self.error_logger_is_built)
                            return False
                    else:
                        try:
                            date_time = datetime.strptime(last_seen[last_seen.find('at'):], "at %I:%M %p")
                            #By default year is 1900 and if time 00.41, minus delta it gets year
                            #1899 and raises an error
                            date_time = date_time.replace(year=datetime.now().year)
                            date_time = date_time - time_delta
                            user_data['last_visit'] = 'last seen ' + date_time.strftime(last_seen[:last_seen.find('at')]+"at %H:%M")
                            if ('yesterday' in last_seen) and (date_time.hour-hours_delta < 0):
                                user_data['last_visit'] = user_data['last_visit'].replace('yesterday','today')
                            elif ('today' in last_seen) and (date_time.hour+hours_delta > 23):
                                user_data['last_visit'] = user_data['last_visit'].replace('today','yesterday')
                        except:
                            self.error_counter += 1
                            self.last_error = 'Error while parsing time in last_seen'
                            self.error_logger_is_built = WriteErrorLog(self.last_error, self.error_logger_is_built)
                            return False

                elif last_seen.lower()=='online':
                    user_data['online']=True
                    user_data['last_visit']='Online'
                    if user_data['mobile_version']:
                        user_data['last_visit'] += ' [Mobile]'
                else:#print raw last_seen data
                    user_data['last_visit'] = 'last seen ' + last_seen#+' That is raw data!'
            else:
                user_data['online']=True
                user_data['last_visit']='Online'
                if user_data['mobile_version']:
                        user_data['last_visit'] += ' [Mobile]'

        except:
            self.error_counter += 1
            self.last_error = "Could not determine user's online status."
            self.error_logger_is_built = WriteErrorLog(self.last_error, self.error_logger_is_built)
            return False

        #Secondary data fectching

        #set object user_data
        self.user_data = user_data

    ######Logging part######
    def ShowWriteInfo(self):
        #if there's new user data,  a new status or online changed from False to True or True to False
        #write the new log to file
        self.PrepareLog()
        if (self.user_data['online']!=self.prev_user_data['online']) or (self.user_data['status']!=self.prev_user_data['status']):
            if self.debug_mode:
                WriteDebugLog('Writing log to file')
            try:
                #increase logs counter
                self.logs_counter += 1
                filename = time.strftime('%Y.%m.%d') + '-' + self.user_data['name'] + '.log'
                self.data_logger_is_built = WriteDataLog(self.log, filename, self.data_logger_is_built)
            except:
                self.error_counter += 1
                self.last_error = 'Could not write Data log to file'
                self.error_logger_is_built = WriteErrorLog(self.last_error, self.error_logger_is_built)
                return False
            #Save previous data
            #update last user_data to the current one
            self.prev_user_data = self.user_data
        try:
            if self.debug_mode:
                WriteDebugLog('Output to console')
            ConsoleLog(self.console_log)
        except:
            self.error_counter += 1
            self.last_error = 'Could not output log to console.'
            self.error_logger_is_built = WriteErrorLog(self.last_error, self.error_logger_is_built)
            pass

    #######################################END logging#######################################

    def SingleRequest(self):
        ConsoleLog('Fetching user data...')
        if self.debug_mode:
            WriteDebugLog('Start single request')
        self.CookSoup()
        self.GetUserData()
        
        #Clear screen
        os.system( [ 'clear', 'cls' ][ os.name == 'nt' ] )

        self.ShowWriteInfo()
        if self.debug_mode:
            WriteDebugLog('Finished single request')

    def Work(self):
        if self.debug_mode:
            WriteDebugLog('Begin work')
        while True:
            self.SingleRequest()
            time.sleep(self.time_step)
