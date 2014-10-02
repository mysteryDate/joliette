#!/usr/bin/python

import httplib2
import pdb
import base64
import time

from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run

class Monitor():
	"""
	A monitor for our gmail inbox
	"""

	__maxHistoryId = 0	# The most recent historical change

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
			userId='me', startHistoryId=self.__maxHistoryId).execute()
		self.__maxHistoryId = self.recentThreads['historyId']

	# def start(self):
	# 	"""
	# 	Starts monitoring the inbox
	# 	"""
		
gmail = Monitor()
while True:
	gmail.update()
	if gmail.recentThreads.has_key('history'):
		pdb.set_trace()
		for thread in gmail.recentThreads['history']:
			messageId = thread['messages'][0]['id']
			newMessage = gmail.service.users().messages().get(
				userId='me', id=messageId).execute()
			messageText = newMessage['payload']['body']['data']
			messageText = base64.urlsafe_b64decode(messageText.encode('UTF'))
			print messageText.strip('\r\n ').split('======')[0]
		# pdb.set_trace()
	time.sleep(2)














