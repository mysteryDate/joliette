#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
A liason between the gmonitor and oF slideshow
"""

import pdb
import random

import gmonitor
import socket
import time
import imaplib2

import calendar

UDP_IP = "127.0.0.1"
UDP_PORT = 7011

MATCH_LABEL = "SMS"
FILTERED_LABELS = ["Refuser", "RefuserAutomatique", "TRASH"]

RESPONSE = u"Merci pour ton message! Regarde bien, il apparaîtra sous peu sur la Grande Carte Blanche! :)"

gmail = gmonitor.Monitor(MATCH_LABEL, FILTERED_LABELS, verbose=True)
# gmail.load("message_database.xml")
PROGRAM_START_TIME = time.time()
NO_REPEAT_LENGTH = 5
EXCLUDED_MESSAGES = []

def GetNextMessage(excluded_messages):
    """
    A helper function to find the best message to next display
    Probably too bruteforcey
    """
    start_time = time.time()
    max_ratio = 0
    best_id = gmail.database.keys()[0]
    for message in gmail.database.values():
        if message in excluded_messages:
            continue
        sent_time = time.strptime(message.time, "%a, %d %b %Y %H:%M:%S +0000")
        time_since_sent = calendar.timegm(time.gmtime()) - calendar.timegm(sent_time)
        time_since_displayed = float('inf')
        if message.last_displayed != "None": # The message has never been displayed
            displayed_time = time.strptime(message.last_displayed, "%a, %d %b %Y %H:%M:%S +0000")
            time_since_displayed = calendar.timegm(time.gmtime()) - calendar.timegm(displayed_time)
        ratio = float(time_since_displayed) / time_since_sent
        if ratio > max_ratio:
            max_ratio = ratio
            best_id = message.id
    print time.time() - start_time
    return gmail.database[best_id]


while True:
    gmail.update()
    input_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
    input_sock.bind(((UDP_IP), UDP_PORT+1))

    data, addr = input_sock.recvfrom(1024)
    if data == "New message please!": #oF wants a message to display
        if len(gmail.database) == 0:
            continue
        if len(gmail.messages_to_add) > 0:
            message_object = gmail.messages_to_add.pop(0)
        else:
            message_object = GetNextMessage(EXCLUDED_MESSAGES)

        phone = message_object.sender
        # Add dashes to phone number
        phone = ('-').join([phone[3:6], phone[6:]]) 
        output = phone + ": " + message_object.message

        output_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        output_sock.sendto(output.encode('utf-8'), (UDP_IP, UDP_PORT))

        output_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
        # Keep things in UTC
        message_object.last_displayed = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
        EXCLUDED_MESSAGES.append(message_object)
        if len(EXCLUDED_MESSAGES) > NO_REPEAT_LENGTH:
            EXCLUDED_MESSAGES.pop(0)

    if time.time() - PROGRAM_START_TIME > 900: # 15 minutes
        gmail.save("message_database.xml")
        # re-initialize the monitor
        gmail = gmonitor.Monitor(MATCH_LABEL, FILTERED_LABELS, verbose=True)
        gmail.load("message_database.xml")
        time.sleep(10) # seems like a good idea
        PROGRAM_START_TIME = time.time()

    if data == "Start":
        gmail = gmonitor.Monitor(MATCH_LABEL, FILTERED_LABELS, verbose=True)

    if data == "Shutdown":
        gmail.save("message_database.xml")
        break

    if data == "Rebuild":
        gmail.save("message_database.xml")
        # re-initialize the monitor
        gmail = gmonitor.Monitor(MATCH_LABEL, FILTERED_LABELS, verbose=True)
        gmail.load("message_database.xml")
        PROGRAM_START_TIME = time.time()

    time.sleep(2)

pdb.set_trace()

# Get time in RFC 2822 Internet email standard:
# time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

# get stored time as struct
# time.strptime(<MESSAGE_OBJECT>.time, "%a, %d %b %Y %H:%M:%S +0000")

# get time differences in seconds between TIME1 and TIME2
# calendar.timegm(<TIME1>) - calendar.timegm(<TIME2>)
