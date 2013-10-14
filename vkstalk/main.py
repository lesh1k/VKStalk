#ptyhon modules
import time #used for time.sleep()
import logging
import os


#modules for retrieving and logging data
from logger import CreateLogFolders, WriteLog, WriteErrorLog, WriteDebugLog
from scrapper import CookSoup, GetUserData

#Global variables
USER_DATA = {}
PREV_DATA = {}
TIME_STEP = 30
LAST_LOG = ''
NEW_LOG = ''
LAST_ERROR = 'No errors yet =)'
ERROR_COUNTER = 0
LOGS_COUNTER = 0
PROGRAM_VERSION = "VKStalk ver. 4.0.0 ALPHA"


if __name__ == '__main__':
	#Print program version
	print PROGRAM_VERSION
	#Keyboard input of user ID
	user_ID = raw_input('User ID:') #e.g."83029348"

	#Print greeting message
	print 'VKStalk successfully launched! Have a tea and analyze the results ;)'

	while True:
		soup = CookSoup(user_ID)
		if not soup:
			USER_DATA=''
			if '[Connection Error]' not in LAST_LOG:
				LAST_LOG = "[Connection Error!!!]  --  " + LAST_LOG
		else:
			USER_DATA=GetUserData(soup)

#Set the refresh rate (how often the logs will be written).
		CreateLogFolders()
		if USER_DATA == "":
			TIME_STEP = 15
		elif WriteLog('',USER_DATA):
			TIME_STEP = 45
		else:
			TIME_STEP = 180

		#Print the data
		logging.basicConfig(level=logging.INFO,
							format='User ID: '+user_ID+'.\nUser Name: '+USER_DATA['name']+
							'\nSince the program was run - ['+str(LOGS_COUNTER)+
							'] logs were written and ['+str(ERROR_COUNTER)+'] errors occurred'+
							'\nLatest log:\n\n'+
							'%(asctime)s%(message)s'+'Last error:'+LAST_ERROR,
							datefmt='>>>Date: %d-%m-%Y. Time: %H:%M:%S \n\n')
		
		NEW_LOG = (USER_DATA['name']+'  --  '+
				  USER_DATA['last_visit']+
				  '\nStatus: '+USER_DATA['status']+'\n\n'
				  )
		logging.warning(NEW_LOG)#warning because no higher level logs were printing to console
		time.sleep(TIME_STEP)
		#Clear screen
		os.system( [ 'clear', 'cls' ][ os.name == 'nt' ] )
		#Print program version
		print PROGRAM_VERSION