import codecs
import os
import glob
import pprint
import string

#get to logs folder
os.chdir('Logs')
#get all log files list
FILE_LIST = glob.glob('*Starovoit.log')
ALL_STATUSES = []
UNIQUE_STATUSES = []
UGLY_RESULT = []
RESULT = {}
DATA = {}
#get the list of statuses per file. [decoded]
for fileName in FILE_LIST:
	fHandle = open(fileName, 'r')
	fData = fHandle.readlines()
	fHandle.close()
	statusesList = []

	for line in fData:
		if 'Status:' in line:
			decodedString = codecs.decode(line.replace('Status: ', ''),'utf8')
			decodedString = decodedString.rstrip()
			statusesList.append(decodedString)
			ALL_STATUSES.append(decodedString)

	DATA[fileName.split('-I')[0]] = statusesList

#Create the list of unique statuses
UNIQUE_STATUSES = list(set(ALL_STATUSES))

#Generate the list of tuples (nr_repetitions, status)
for status in UNIQUE_STATUSES:
	UGLY_RESULT.append((ALL_STATUSES.count(status), status))

#Sort the result descendingly depending on nr. of occurences
UGLY_RESULT.sort()
UGLY_RESULT.reverse()

#Create a beautiful result
for i in range(len(UGLY_RESULT)):
	RESULT[i+1] = UGLY_RESULT[i]

#write result to file
#get to initial folder
os.chdir('..')
fHandle = open('summary.log', 'w')

for key in RESULT.keys():
	fHandle.write("%6d. %s \t  [x%d]\n" %(key, codecs.encode(string.ljust(RESULT[key][1],150), 'utf8'), RESULT[key][0]) )
fHandle.close()

#== u'Not_Found\n'

#initialize pretty print object
# pp = pprint.PrettyPrinter(indent = 4)
# print DATA['2013.4.10'][100]