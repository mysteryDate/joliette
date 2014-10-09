#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
A suite for testing the effect of wait time
"""

import pdb

import gmonitor
import socket
import time

from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run
from email.mime.text import MIMEText
import httplib2
import base64

UDP_IP = "127.0.0.1"
UDP_PORT = 7011

MATCH_LABEL = "SMS"
FILTERED_LABELS = ["Refuser", "RefuserAutomatique", "TRASH"]

gmail = gmonitor.Monitor(MATCH_LABEL, FILTERED_LABELS, verbose=True)
gmail.load("message_database.xml")
gmail.update()
# gmail.save("message_database.xml")

# set up a second gmail
CLIENT_SECRET_FILE_2 = 'client_secret_2.json'

# Check https://developers.google.com/gmail/api/auth/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.modify'

# Location of the credentials storage file
STORAGE = Storage('gmail2.storage')

# Start the OAuth flow to retrieve credentials
flow = flow_from_clientsecrets(CLIENT_SECRET_FILE_2, scope=OAUTH_SCOPE)
http = httplib2.Http()

# Try to retrieve credentials from storage or run the flow to generate them
credentials = STORAGE.get()
if credentials is None or credentials.invalid:
    credentials = run(flow, STORAGE, http=http)

# Authorize the httplib2.Http object with our credentials
http = credentials.authorize(http)

# Build the Gmail service from discovery
gmail2 = build('gmail', 'v1', http=http)
results = {}
wait_time = 0.5

def send_text():
    message_text = u"wait_time = " + unicode(wait_time)
    response = MIMEText(message_text.encode('utf-8'))
    response['to'] = "4509446635@@desksms.appspotmail.com"
    response['from'] = "krajeski@gmail.com"
    response = {'raw': base64.b64encode(response.as_string())}
    try:
        gmail2.users().messages().send(userId='me', body=response).execute()
    except Exception as e: 
        print(e)

send_text()
ptr_time = time.time()
while True:
    gmail.update()
    if len(gmail.messages_to_add) > 0:
        message_object = gmail.messages_to_add.pop(0)

        # try:
        #     gmail.respond(message_object.id, RESPONSE)
        # except Exception as e: print (e)

        phone = message_object.sender
        # Add dashes to phone number
        phone = ('-').join([phone[:3], phone[3:6], phone[6:]]) 
        output = phone + ": " + message_object.message

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(output.encode('utf-8'), (UDP_IP, UDP_PORT))

        results[wait_time] = time.time() - ptr_time
        wait_time += 0.1
        send_text()
        ptr_time = time.time()
    time.sleep(wait_time)

pdb.set_trace()