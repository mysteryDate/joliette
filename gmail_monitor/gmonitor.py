#!/usr/bin/python
"""
A monitor for a gmail inbox using the gmailAPI
"""

import httplib2
import pdb
import base64
import traceback
# import time

# for creating xml files
from lxml import etree

# for reading from gmail
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run

class Monitor():
    """
    A monitor for our gmail inbox
    """

    # SMS labels, TODO make this more general
    SMS_LABEL = "Label_8"
    TRASH = "TRASH"
    REFUSED_LABEL = "Label_3"
    AUTOMATIC_REFUSED_LABEL = "Label_5"
    FILTERED_LABELS = [TRASH, REFUSED_LABEL, AUTOMATIC_REFUSED_LABEL]
    __maxHistoryId = 0  # The most recent historical change
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
        To alleviate server errors, it skips sometimes
        """
        try:
            self.recentThreads = self.service.users().history().list(
                userId='me', startHistoryId=self.__maxHistoryId, labelId=self.SMS_LABEL).execute()
            self.__maxHistoryId = self.recentThreads['historyId']
        except Exception as e: print (e)

    def add_message_to_database(self, messageId):
        """
        Takes the id of an inbox message, requests it and adds it to the database
        """
        newMessageEntry = Message()
        try:
            newMessageData = self.service.users().messages().get(userId='me', id=messageId).execute()
        except Exception as e: 
            print (e)
            traceback.print_exc()
            return
        if any([_ for _ in newMessageData['labelIds'] if _ in self.FILTERED_LABELS]):
            newMessageEntry.active = False
        else:
            newMessageEntry.active = True
        for entry in newMessageData['payload']['headers']:
            if entry['name'] == 'Date':
                newMessageEntry.time = entry['value']
        text = newMessageData['payload']['body']['data']
        text = base64.urlsafe_b64decode(text.encode('UTF'))
        newMessageEntry.message = text.strip('\r\n ').split('====')[0].rstrip(
            '\r\n ').replace(' \r\n', '').replace('\r\n', '')
        self.database[messageId] = newMessageEntry

    def populate(self):
        """
        Get recent relevant messages
        """
        # TODO automate the q= section
        try:
            messages = self.service.users().messages().list(
                userId='me', labelIds=self.SMS_LABEL,
                q="-label:{Refuser RefuserAutomatique}").execute()
        except Exception as e: print (e)
        if messages['messages']:
            for message in messages['messages']:
                self.add_message_to_database(message['id'])

    def print_database(self):
        """
        Print the current database to the terminal
        """
        print "\tId\t\t|Active\t|\tTime\t\t|\tMessage\t"
        print "------------------------------------------"
        for messageId in self.database.keys():
            mess = self.database[messageId]
            print messageId, "\t|", mess.active, "\t|", mess.time, "\t|", mess.message

class Message():
    """
    A text message received into the mailbox
    """
    def __init__(self):
        self.active = False # Whether we want to display the message
        self.time = "" # Gmail reports in GM time, so I don't want to do time.ctime()
        self.message = ""

def create_external_db(database):
    """
    Pass it the database of a Monitor
    """
    db = etree.Element("DATABASE")
    for messageId in database.keys():
        message = database[messageId]
        elem = etree.SubElement(db, "MESSAGE")
        idNum = etree.SubElement(elem, "ID")
        activeValue = etree.SubElement(elem, "ACTIVE")
        time = etree.SubElement(elem, "TIME_RECEIVED")
        messageText = etree.SubElement(elem, "MESSAGE_TEXT")
        idNum.text = messageId
        activeValue.text = str(message.active)
        time.text = message.time
        messageText.text = unicode(message.message, 'utf-8')
    tree = etree.ElementTree(db)
    tree.write("message_database.xml", encoding="UTF-8", pretty_print=True)

def read_external_db(monitor, filepath):
    """
    Read in an external database
    """
    tree = etree.parse(filepath)
    for entry in tree.findall('MESSAGE'):
        newMessage = Message()
        newId = unicode(entry.find("ID").text)
        newMessage.active = bool(entry.find("ACTIVE").text)
        newMessage.time = unicode(entry.find("TIME_RECEIVED").text)
        newMessage.message = entry.find("MESSAGE_TEXT").text
        monitor.database[newId] = newMessages

# "Label_3" = "Refuser"
# "Label_5" = "RefuserAutomatique"
# "Label_6" = "Notes"
# "Label_7" = "Accepter"
# "Label_8" = "SMS"

# Other system labels
# 'DRAFT'
# 'CATEGORY_UPDATES'
# 'UNREAD'

# message['payload']['headers'] is an array of dictionaries,
# one will have key 'date' and value the time in GMT (were -5)