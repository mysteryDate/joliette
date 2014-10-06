import gmonitor
import time
import pdb

def main():
    gmail = gmonitor.Monitor()

    while(True):
        gmail.update()
        # something changed
        if gmail.recentThreads.has_key('history'):
            modifiedMessages = set()
            # Get unique ids for every changed message
            for thread in gmail.recentThreads['history']:
                if thread.has_key('messages'):
                    for message in thread['messages']:
                        modifiedMessages.add(message['id'])
            for messageId in modifiedMessages:
                # Check to see if it's moved to or from a filtered folder
                if messageId in gmail.database:
                    print messageId, "\t|", gmail.database[messageId].message
                    messageData = gmail.service.users().messages().get(
                        userId='me', id=messageId, format='minimal').execute()
                    if any([_ for _ in messageData['labelIds'] if _ in gmail.FILTERED_LABELS]):
                        gmail.database[messageData['id']].active = False
                        print "Deactivated"
                    else:
                        gmail.database[messageData['id']].active = True
                        print "Activated"
                # Then it must be new
                else:
                    gmail.add_message_to_database(messageId)
                    try:
                        print messageId, "\t|", gmail.database[messageId].message, "| Added"
                    except:
                        print messageId, " not found"
        time.sleep(0.5)

main()