from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json heyo heyo heyo
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def addeventlist():
    # add list of events to calendar
    return None:

# https://developers.google.com/calendar/create-events
def addevent(date,start,end):
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    GMT_OFF = '-05:00'    # PDT/MST/GMT-7
    EVENT = {
        'summary': 'Coffee Break and Chat',
        #'location': asdf,
        #datetime format:'2015-09-15T00:00:00%s' % GMT_OFF
        'start':   {'dateTime': date + 'T'+ start+ '%s' % GMT_OFF},
        'end':     {'dateTime': date + 'T'+ end+ '%s' % GMT_OFF},
        #'attendees': [
        #   { 'email': email1 },
        #   { 'email': email2 },
        # ]
    }
    e = service.events().insert(calendarId='primary',
    sendNotifications=True, body=EVENT).execute()
    # batch = service.new_batch_http_request(callback = cb_insert_event)
    # batch.add(service.events()...body=EVENT)
    # ...
    # batch.execite(http=http)
    # https://gist.github.com/afunTW/bf958eea15835d14aa976990d1f0bb88
    # or do this one below
    # http://wescpy.blogspot.com/2015/09/creating-events-in-google-calendar.html 
    print('''*** %r event added:
    Start: %s
    End:   %s''' % (e['summary'].encode('utf-8'),
        e['start']['dateTime'], e['end']['dateTime']))
        
run(host='localhost', port=8083, debug=True)