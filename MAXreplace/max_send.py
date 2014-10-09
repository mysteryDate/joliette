#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
A liason between GMontior and previously written maxpatch
"""

import gmonitor
from sys import getsizeof
import simpleOSC as osc
import thread
import time
import pdb

MATCH_LABEL = "SMS"
FILTERED_LABELS = ["Refuser", "RefuserAutomatique", "TRASH"]

UDP_IP = "127.0.0.1"
UDP_PORT = 7006

RESPONSE = u"Merci pour ton message! Regarde bien, il apparîtra sous peu sur la Grande Carte Blanche! :)"

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

def monitor_inbox(foo, bar):
    while True:
        gmail.update()
        time.sleep(2)

def pass_on_messages(foo, bar):
    while True:
        if len(gmail.messages_to_add) > 0:
            mess = gmail.messages_to_add.pop(0)
            send_to_max(mess, "/aj")
        if len(gmail.messages_to_delete) > 0:
            mess = gmail.messages_to_delete.pop(0)
            send_to_max(mess, "/del")

for message in gmail.database.values():
    send_to_max(message, "/aj")

thread.start_new_thread(monitor_inbox, ("foo", "bar"))
thread.start_new_thread(pass_on_messages, ("foo", "bar"))

while 1:
    pass

# pdb.set_trace()