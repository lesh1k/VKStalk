#ptyhon modules
import logging
import time #used for time.sleep()
import os #to check if a file exists

def CreateLogFolders():
	#Creates the following tree if not present yet:
	#Data-> [Logs, Errors, Debug]
	current_path = '/'.join(__file__.split('/')[:-1])
	data_folder = os.path.join(current_path, "Data")
	error_folder = os.path.join(current_path, "Data/Errors")
	logs_folder = os.path.join(current_path, "Data/Logs")
	debug_folder = os.path.join(current_path, "Data/Debug")

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

def WriteLog(log, user_data):
	#Writes the log to the respective file. Creates the file if 
	#necessary
	current_path = '/'.join(__file__.split('/')[:-1])
	filename = time.strftime('%Y.%m.%d') + '-' + user_data['name'] + '.log'
	path = os.path.join(current_path, "Data/Logs/"+filename)
	logging.basicConfig(filename=path, filemode='a', level=logging.INFO,
						format='%(asctime)s%(message)s',
						datefmt='>>>Date: %d-%m-%Y. Time: %H:%M:%S \n\n')
	logger = logging.getLogger('data_logger')
	logger.setLevel(logging.INFO)

	if not os.path.exists(path):#first log to file
		general_info = ('Log file created on' + time.strftime(' %d-%B-%Y at %H:%M:%S') +
						'\nUsername: '+user_data['name'] +
						'\nStatus: ' + user_data['status'] + 
						'\nBirthday: ' + user_data['birthday'] + 
						'\nSkype: ' + user_data['skype'] + 
						'\nSite: ' + user_data['site'] + 
						'\nLast visit: ' + user_data['last_visit'] + 
						'\nTwitter: ' + user_data['twitter'] + 
						'\nInstagram: ' + user_data['instagram'] + 
						'\nFacebook: ' + user_data['facebook'] + 
						'\nPhone: ' + user_data['phone'] +
						'\nUniversity: ' + user_data['university'] +
						'\nPhoto: ' + user_data['photo'] +
						'\nNumber of photos: ' + user_data['number_of_photos'] +
						'\nNumber of posts: ' + user_data['number_of_posts'] +
						'\nNumber of gifts: ' + user_data['number_of_gifts'] +
						'\nNumber of friends: ' + user_data['number_of_friends'] +
						'\n\n\n\n'
						)
		fHandle = open(path,'w')
		fHandle.write(general_info)
		fHandle.close()
	
	#Common log to file	
	log = (user_data['name'] + '  --  ' +
		  user_data['last_visit'] +
		  '\nStatus: ' + user_data['status'] + '\n\n\n\n'
		  )
	try:
		logger.info(log)
	except:
		#Here be the Error logging line#
		return False
	
	return True

def WriteErrorLog(message):
	#Writes the error log to the respective file

	current_path = '/'.join(__file__.split('/')[:-1])
	filename = 'ERRORS -' + time.strftime('%Y.%m.%d') + '.log'
	path = os.path.join(current_path, "Data/Errors/"+filename)
	logging.basicConfig(filename=path, filemode='a', level=logging.ERROR,
						format='%(levelname)s - %(asctime)s%(message)s\n\n\n',
						datefmt='[Date: %d-%m-%Y. Time: %H:%M:%S]\n')

	if not os.path.exists(path):#first log to file
		fHandle = open(path,'w')
		fHandle.close()
	
	try:
		logging.error(message)
	except:
		#Here be the Error logging line#
		return False
	
	return True


def WriteDebugLog(message):
	#Writes the debug log to the respective file
	
	current_path = '/'.join(__file__.split('/')[:-1])
	filename = 'DEBUG -' + time.strftime('%Y.%m.%d') + '.log'
	path = os.path.join(current_path, "Data/Debug/"+filename)
	logging.basicConfig(filename=path, filemode='a', level=logging.DEBUG,
						format='%(levelname)s - %(asctime)s%(message)s\n',
						datefmt='[Date: %d-%m-%Y. Time: %H:%M:%S] - ')

	if not os.path.exists(path):#first log to file
		fHandle = open(path,'w')
		fHandle.close()
	
	try:
		logging.debug(message)
	except:
		#Here be the Error logging line#
		return False
	
	return True