#!/usr/bin/python
"""
A liason between the gmonitor and oF slideshow
"""

import pdb

import gmonitor
import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 7011

MATCH_LABEL = "SMS"
FILTERED_LABELS = ["Refuser", "RefuserAutomatique", "TRASH"]

gmail = gmonitor.Monitor(MATCH_LABEL, FILTERED_LABELS, verbose=True)
gmail.load("message_database.xml")

# while True:
#     gmail.update()
#     if len(gmail.messages_to_add) > 0:
#         message_object = gmail.messages_to_add.pop(0)
#         phone = message_object.sender
#         # Add dashes to phone number
#         phone = ('-').join([phone[:3], phone[3:6], phone[6:]]) 
#         output = phone + ": " + message_object.message

#         sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         sock.sendto(output.encode('utf-8'), (UDP_IP, UDP_PORT))

pdb.set_trace()