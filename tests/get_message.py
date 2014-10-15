import calendar
import time
import gc
import pdb
import random

import plotly.plotly as py
from plotly.graph_objs import *
py.sign_in("mysteryDate", "a6fd7sm5jr")

class Message():
    """
    A text message received into the mailbox
    """
    def __init__(self):
        self.id = "" # The gmail id of the message, will also be its key in the database
        self.sender = "" # The phone number of the sender
        self.time = "" # Gmail reports in GM time, so I don't want to do time.ctime()
        self.message = ""
        self.last_displayed = "" # The most recent time we displayed the message      

def GetNextMessage():
    """
    A helper function to find the best message to next display
    Probably too bruteforcey
    """
    # start_time = time.time()
    max_ratio = 0
    best_id = database.keys()[0]
    for message in database.values():
        sent_time = time.strptime(message.time, "%a, %d %b %Y %H:%M:%S +0000")
        time_since_sent = calendar.timegm(time.gmtime()) - calendar.timegm(sent_time)
        displayed_time = time.strptime(message.last_displayed, "%a, %d %b %Y %H:%M:%S +0000")
        time_since_displayed = calendar.timegm(time.gmtime()) - calendar.timegm(displayed_time)
        ratio = float(time_since_displayed) / time_since_sent
        if ratio > max_ratio:
            max_ratio = ratio
            best_id = message.id
    return database[best_id]

database = {}
results = {}
MAX_SIZE = 1000

for size in range(MAX_SIZE):
    # Initialize
    # pdb.set_trace()
    new_message = Message()
    new_id = 0
    while True:
        new_id = random.randrange(MAX_SIZE**2)
        if new_id not in database:
            break
    new_message.id = new_id
    now = time.time()
    now += random.randrange(-15000000, 15000000)
    new_message.time = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(now))
    now += random.randrange(30000000)
    new_message.last_displayed = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(now))
    database[new_message.id] = new_message
    # test 
    gc.disable()
    ptr_time = time.time()
    GetNextMessage()
    results[size + 1] = time.time() - ptr_time
    gc.enable()
    print size

for entry in results:
    print entry, results[entry]

trace = Scatter(x=results.keys(), y=results.values())
data = Data([trace])
plot_url = py.plot(data, filename='get_message')