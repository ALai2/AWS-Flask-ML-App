# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
from __future__ import print_function
import datetime
import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json heyo heyo heyo
SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def addeventlist():
    # add list of events to calendar
    # use batch?
    return None

# https://developers.google.com/calendar/create-events 
# http://wescpy.blogspot.com/2015/09/creating-events-in-google-calendar.html 
def addevent(mylist):
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    creds = get_credentials()

    service = build('calendar', 'v3', credentials=creds)
    GMT_OFF = '-05:00'    # PDT/MST/GMT-7
    
    for i in mylist:
        EVENT = {
            'summary': i['name'],
            #'location': asdf,
            #datetime format:'2015-09-15T00:00:00%s' % GMT_OFF
            'start':   {'dateTime': i['date'] + 'T'+ i['start'] + '%s' % GMT_OFF},
            'end':     {'dateTime': i['date'] + 'T'+ i['end'] + '%s' % GMT_OFF},
            'attendees': [
              { 'email': i['email1'] },
              { 'email': i['email2'] },
            ]
        }
        e = service.events().insert(calendarId='primary',
        sendNotifications=True, body=EVENT).execute()

        # print('''*** %r event added:
        # Start: %s
        # End:   %s''' % (e['summary'].encode('utf-8'),
        #     e['start']['dateTime'], e['end']['dateTime']))

# if __name__ == '__main__':
#     mylist = []
#     d1 = {'name': 'Testing', 'date': '2019-06-14', 'start': '19:00:00', 'end': '22:00:00', 'email1': 'al766@cornell.edu', 'email2': 'al766@cornell.edu'}
#     d2 = {'name': 'Testing', 'date': '2019-06-14', 'start': '15:00:00', 'end': '17:00:00', 'email1': 'al766@cornell.edu', 'email2': 'al766@cornell.edu'}
#     mylist.append(d1)
#     mylist.append(d2)
#     addevent(mylist)