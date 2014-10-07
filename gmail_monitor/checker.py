import gmonitor
import time
import pdb

def main():
    gmail = gmonitor.Monitor()
    # Get in most recent database
    gmonitor.read_external_db(gmail, "message_database.xml")

    while(True):
        gmail.update()
        # pdb.set_trace()
        # something changed
        if gmail.recentThreads.has_key('history'):
            modifiedMessages = set()
            # Get unique ids for every changed message
            for thread in gmail.recentThreads['history']:
                if thread.has_key('messages'):
                    for message in thread['messages']:
                        modifiedMessages.add(message['id'])
            print "Number of new messages:", len(modifiedMessages)
            for messageId in modifiedMessages:
                # Check to see if it's moved to or from a filtered folder
                if messageId in gmail.database:
                    report_string = str(messageId)+"\t| "+gmail.database[messageId].message+"\t|"
                    status = "Unchanged"
                    # pdb.set_trace()
                    try:
                        messageData = gmail.service.users().messages().get(
                            userId='me', id=messageId, format='minimal').execute()
                        if any([_ for _ in messageData['labelIds'] if _ in gmail.FILTERED_LABELS]):
                            if gmail.database[messageData['id']].active == True:
                                gmail.database[messageData['id']].active = False
                                status = "Deactivated"
                        else:
                            if gmail.database[messageData['id']].active == False:
                                gmail.database[messageData['id']].active = True
                                status = "Activated"
                    except:
                        # It was fully deleted
                        status = "Deleted"
                        del gmail.database[messageId]
                    if status != "Unchanged":
                        print report_string, status
                # Then it must be new
                else:
                    if gmail.add_message_to_database(messageId):
                        print messageId, "\t|", gmail.database[messageId].message, "\t| Added"
        time.sleep(0.5)

main()
