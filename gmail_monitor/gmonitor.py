#!/usr/bin/python

import httplib2
import pdb
import base64
import time

# for creating xml files
from lxml import etree

# for reading from gmail
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run

# SMS label
SMS_LABEL = "Label_8"
TRASH = "TRASH"
REFUSED_LABEL = "Label_3"
AUTOMATIC_REFUSED_LABEL = "Label_5"
FILTERED_LABELS = [TRASH, REFUSED_LABEL, AUTOMATIC_REFUSED_LABEL]

class Monitor():
    """
    A monitor for our gmail inbox
    """

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
        """
        self.recentThreads = self.service.users().history().list(
            userId='me', startHistoryId=self.__maxHistoryId, labelId=SMS_LABEL).execute()
        self.__maxHistoryId = self.recentThreads['historyId']

    def addMessageToDatabase(self, messageId):
        """
        Takes the id of an inbox message, requests it and adds it to the database
        """
        newMessageEntry = Message()
        newMessageData = self.service.users().messages().get(userId='me', id=messageId).execute()
        if any([_ for _ in newMessageData['labelIds'] if _ in FILTERED_LABELS]):
            return
        newMessageEntry.active = True
        for entry in newMessageData['payload']['headers']: 
            if entry['name'] == 'Date':
                newMessageEntry.time = entry['value']
        text = newMessageData['payload']['body']['data']
        text = base64.urlsafe_b64decode(text.encode('UTF'))
        newMessageEntry.message = text.strip('\r\n ').split('====')[0].rstrip('\r\n ').replace(' \r\n', '').replace('\r\n', '')
        self.database[messageId] = newMessageEntry

    def populate(self):
        """
        Get recent relevant messages
        """
        messages = self.service.users().messages().list(
            userId='me', labelIds=SMS_LABEL,
            q="-label:{Refuser RefuserAutomatique}").execute()
        if messages['messages']:
            for message in messages['messages']:
                self.addMessageToDatabase(message['id'])

    def printDatabase(self):
        """
        Print the current database to the terminal
        """
        print "\tId\t\t|Active\t|\tTime\t\t|\tMessage\t"
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
        monitor.database[newId] = newMessage 

pdb.set_trace()

# gmail.populate()
# gmail.printDatabase()
# while True:
#   gmail.update()
#   # something changed
#   if gmail.recentThreads.has_key('history'):
#       modifiedMessages = set()
#       # Get unique ids for every changed message
#       for thread in gmail.recentThreads['history']:
#           if thread.has_key('messages'):
#               for message in thread['messages']:
#                   modifiedMessages.add(message['id'])
#       for messageId in modifiedMessages:
#           # Check to see if it's moved to or from a filtered folder
#           if messageId in gmail.database:
#               print messageId, "\t|", gmail.database[messageId].message
#               messageData = gmail.service.users().messages().get(
#                   userId='me', id=messageId, format='minimal').execute()
#               if any([_ for _ in messageData['labelIds'] if _ in FILTERED_LABELS]):
#                   gmail.database[messageData['id']].active = False
#                   print "Deactivated"
#               else:
#                   gmail.database[messageData['id']].active = True
#                   print "Activated"
#           # Then it must be new
#           else:
#               gmail.addMessageToDatabase(messageId)
#               print messageId, "\t|", gmail.database[messageId].message
#               print "Added"
#   time.sleep(2)

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












