#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
A liason between the gmonitor and oF slideshow
"""

import pdb

import gmonitor
import socket
import time
import imaplib2

UDP_IP = "127.0.0.1"
UDP_PORT = 7011

MATCH_LABEL = "SMS"
FILTERED_LABELS = ["Refuser", "RefuserAutomatique", "TRASH"]

RESPONSE = u"Merci pour ton message! Regarde bien, il apparaîtra sous peu sur la Grande Carte Blanche! :)"

gmail = gmonitor.Monitor(MATCH_LABEL, FILTERED_LABELS, verbose=True)
gmail.load("message_database.xml")
startTime = time.time()

while True:
    gmail.update()
    if len(gmail.messages_to_add) > 0:
        message_object = gmail.messages_to_add.pop(0)

        # try:
        #     gmail.respond(message_object.id, RESPONSE)
        # except Exception as e: print (e)

        phone = message_object.sender
        # Add dashes to phone number
        phone = ('-').join([phone[3:6], phone[6:]]) 
        output = phone + ": " + message_object.message

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(output.encode('utf-8'), (UDP_IP, UDP_PORT))

        if startTime - time.time() > 900: # 15 minutes
            gmail.save("message_database.xml")
            # re-initialize the monitor
            gmail = gmonitor.Monitor(MATCH_LABEL, FILTERED_LABELS, verbose=True)
            gmail.load("message_database.xml")
            time.sleep(10) # seems like a good idea
            startTime = time.time()

    time.sleep(2)

pdb.set_trace()