#Required modules
import urllib2 #retrieve the page
import codecs #to encode into utf-8 russian characters
import time #used for time.sleep()
import os #to check if a file exists
from bs4 import BeautifulSoup
from threading import Thread
import string
from datetime import datetime, timedelta
import logging

#Class definition
class VKStalk:
#Class description

	def __init__(self, user_id):
		self.user_id = user_id
		self.user_data = {}
		self.prev_user_data = {}
		self.time_step = 30
		self.last_log = ''
		self.log = ''
		self.last_error = 'No errors yet =)'
		self.error_counter = 0
		self.logs_counter = 0
		self.version = "VKStalk ver. 4.0.0 ALPHA"

	def cookSoup(self):
		# Return the soup obtained from scrapping the page or False if any
		# error occured while connecting

		# Target URLs for VK and Mobile VK
			url='http://vk.com/'
			url_mobile='http://m.vk.com/'

		#generate user specific URLs
			if self.user_id.isdigit():
				url += 'id' + self.user_id
				url_mobile += 'id' + self.user_id
			else:
				url +=  self.user_id
				url_mobile += self.user_id

		#requesting the page
			try:
				cHandle = urllib2.urlopen(url)
				self.html = cHandle.read()
				cHandle.close()
			except:
				#Here be the Error logging line#
				# return False
				pass

			#set soup
			self.soup = BeautifulSoup(self.html)

	def getUserData(self):
		# Returns a dictionary with user data
		# The following data is available depending on user-specific
		# security settings: name, photo, isOnline or last visited time, 
		# skype, instagram, facebook, phone_number, university, number
		# of photos, nr of posts on the wall, nr. of audio files, nr. of
		# online friends, some of the friends who are online, nr. of friends
		# nr. of gifts. Some more data is much less relevant.
		
		# Initialize user_data dictionary with default values
		user_data = {}
		#Primary data
		user_data['name'] = '_not_found'
		user_data['status'] = '_not_found'
		user_data['online'] = '_not_found'
		user_data['last_visit'] = '_not_found'
		#Secondary data
		user_data['skype'] = '_not_found'
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

		#:Data fetching
		###:Name
		try:
			user_data['name']=codecs.encode(self.soup.html.head.title.text,'utf8')
			valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)#for filename verification
		
			#Sanitize user name
			for c in user_data['name']:
				if c not in valid_chars:
					user_data['name'] = user_data['name'].replace(c,'')
					
			if user_data['name'][-2:] == 'VK':
				user_data['name'] = user_data['name'][:-2].rstrip()
		except:
			#Here be the Error logging line#
			# return False
			pass

		###:Status
		status = self.soup.find('div', {"class":"status"})
		if status:
			user_data['status'] = status.text
		else:
			status = self.soup.find('div',{'class':'pp_status'})
			if status:
				user_data['status'] = status.text

		###:Online OR not [last seen time]
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
				
				if 'am' in last_seen or 'pm' in last_seen:
					# Set timedelta according to daylight savings time
					if time.localtime().tm_isdst == 1:
						hours_delta = -1
						time_delta = timedelta(hours=hours_delta)
					else:
						hours_delta = -2
						time_delta = timedelta(hours=hours_delta)

					for c in last_seen[:last_seen.find('at')]:
						if c.isdigit():
							date_found = True
							break

					if date_found:
						try:
							date_time = datetime.strptime(last_seen, "%d %B at %I:%M %p")
							date_time = date_time - time_delta
							user_data['last_visit'] = datetime.strftime("last seen on %B %d at %H:%M",date_time)
						except:
							#Here be the Error logging line#
							# return False
							pass
					else:
						try:
							date_time = datetime.strptime(last_seen[last_seen.find('at'):], "at %I:%M %p")
							date_time = date_time - time_delta
							user_data['last_visit'] = datetime.strftime(last_seen[:last_seen.find('at')]+"at %H:%M",date_time)
							if ('yesterday' in last_seen) and (date_time.hour+hours_delta < 0):
								user_data['last_visit'] = user_data['last_visit'].replace('yesterday','today')
						except:
							#Here be the Error logging line#
							# return False
							pass

				elif last_seen.lower()=='online':
					user_data['online']=True
					user_data['last_visit']='Online'			
				else:#print raw last_seen data
					user_data['last_visit']=last_seen#+' That is raw data!'
			else:
			    user_data['online']=True
			    user_data['last_visit']='Online'

		except:
			#Here be the Error logging line#
			# return False
			pass

		#Secondary data fectching

		#set object user_data
		self.user_data = user_data

		def writeLog(self):

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
				# return False
				pass

			#################LOG WRITING#########################