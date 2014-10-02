#!/usr/bin/python

import httplib2
import pdb
import base64
import time

from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run

# SMS label
SMS_LABEL = "Label_8"
TRASH = "TRASH"
REFUSED_LABEL = "Label_3"
ATOMATIC_REUSED_LABEL = "Label_5"

class Monitor():
	"""
	A monitor for our gmail inbox
	"""

	__maxHistoryId = 0	# The most recent historical change
	database = {} # Some message storage

	def __init__(self):
		# Path to the client_secret.json file downloaded from the Developer Console
		CLIENT_SECRET_FILE = 'client_secret.json'

		# Check https://developers.google.com/gmail/api/auth/scopes for all available scopes
		OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.readonly'

		# Location of the credentials storage file
		STORAGE = Storage('gmail.storage')

		# Start the OAuth flow to retrieve credentials
		flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=OAUTH_SCOPE)
		http = httplib2.Http()

		# Try to retrieve credentials from storage or run the flow to generate them
		credentials = STORAGE.get()
		if credentials is None or credentials.invalid:
		  credentials = run(flow, STORAGE, http=http)

		# Authorize the httplib2.Http object with our credentials
		http = credentials.authorize(http)

		# Build the Gmail service from discovery
		self.service = build('gmail', 'v1', http=http)

		# Get the right history id, can always run a threads().list() if you need previous ones
		threads = self.service.users().threads().list(userId='me').execute()

		if threads['threads']:
			for thread in threads['threads']:
				if thread['historyId'] > self.__maxHistoryId:
					self.__maxHistoryId = thread['historyId']

	def update(self):
		"""
		Updates most recent history, return new/modified threads
		"""
		self.recentThreads = self.service.users().history().list(
			userId='me', startHistoryId=self.__maxHistoryId, labelId=SMS_LABEL).execute()
		self.__maxHistoryId = self.recentThreads['historyId']

	def populate(self):
		"""
		Get recent relevant messages
		"""
		messages = self.service.users().messages().list(
			userId='me', labelIds=SMS_LABEL,
			q="-label:{Refuser RefuserAutomatique}").execute()
		if messages['messages']:
			for message in messages['messages']:
				newMessage = Message()
				data = self.service.users().messages().get(
					userId='me', id=message['id']).execute()
				newMessage.active = True
				for entry in data['payload']['headers']:
					if entry['name'] == 'Date':
						newMessage.time = entry['value']
				text = data['payload']['body']['data']
				text = base64.urlsafe_b64decode(text.encode('UTF'))
				newMessage.message = text.strip('\r\n ').split('====')[0].rstrip('\r\n ').replace(' \r\n', '').replace('\r\n', '')
				self.database[message['id']] = newMessage

	def printDatabase(self):
		"""
		Print the current database to the terminal
		"""
		print "\tId\t|Active\t|\tTime\t|\tMessage\t"
		print "------------------------------------------"
		for messageId in self.database.keys():
			mess = self.database[messageId]
			print messageId, "\t|", mess.active,"\t|", mess.time,"\t|", mess.message

class Message():
	"""
	A text message received into the mailbox
	"""
	def __init__(self):
		self.active = False # Whether we want to display the message
		self.time = time.localtime() # Right now!
		self.message = ""

gmail = Monitor()
while True:
	gmail.update()
	# something changed
	if gmail.recentThreads.has_key('history'):
		modifiedMessages = set()
		for thread in gmail.recentThreads['history']:
			if thread.has_key('messages'):
				for message in thread['messages']:
					modifiedMessages.add(message['id'])
		pdb.set_trace()
		print modifiedMessages
	# 	for thread in gmail.recentThreads['history']:
	# 		messageId = thread['messages'][0]['id']
	# 		newMessage = gmail.service.users().messages().get(
	# 			userId='me', id=messageId).execute()
	# 		messageText = newMessage['payload']['body']['data']
	# 		messageText = base64.urlsafe_b64decode(messageText.encode('UTF'))
	# 		print messageText.strip('\r\n ').split('======')[0].rstrip('\r\n ')
		# pdb.set_trace()
	time.sleep(2)

# "Label_3" = "Refuser"
# "Label_5" = "RefuserAutomatique"
# "Label_8" = "SMS"

# message['payload']['headers'] is an array of dictionaries, 
# one will have key 'date' and value the time in GMT (were -5)












