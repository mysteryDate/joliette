#!/usr/bin/python
"""
A liason between GMontior and previously written maxpatch
"""

import gmonitor
from sys import getsizeof
# import socket
import simpleOSC as osc
import pdb

MATCH_LABEL = "SMS"
FILTERED_LABELS = ["Refuser", "RefuserAutomatique"]

UDP_IP = "127.0.0.1"
UDP_PORT = 7011

osc.initOSCClient(ip=UDP_IP, port=UDP_PORT)

def send_to_max(message_object, direction):
    """
    Takes a message object, a direction (e.g. /aj)
    Then proecesses a message to send to max
    """
    phone = message_object.sender
    # Add dashes to phone number
    phone = ('-').join([phone[:3], phone[3:6], phone[6:]]) 
    output = "||" + phone + "||" + message_object.message
    osc.sendOSCMsg(address=direction, data=[output.encode('utf-8')])


gmail = gmonitor.Monitor(MATCH_LABEL, FILTERED_LABELS, verbose=True)
gmail.load("message_database.xml")

entry = gmail.database.values()[0]
send_to_max(entry, '/aj')

pdb.set_trace()