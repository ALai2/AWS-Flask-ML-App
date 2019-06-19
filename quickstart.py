from __future__ import print_function
from datetime import datetime, timedelta
import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
from dateutil import tz

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json heyo heyo heyo
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_credentials():
    """ Gets valid user credentials from storage.
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    Returns: Credentials, the obtained credential.
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

# input is a dictionary which represents an event to be added to google calendar
def addevent(event, service):
    utc_zone = tz.tzutc()
    local_zone = tz.tzlocal()
    
    # convert datetime from local time zone to utc time zone
    # event start time
    start_date = event['date'] + 'T'+ event['start']
    start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S")
    start_date = start_date.replace(tzinfo=local_zone)
    utc_start = start_date.astimezone(utc_zone)
    utc_start = datetime.strftime(utc_start, "%Y-%m-%dT%H:%M:%S-00:00")

    # event end time
    end_date = event['date'] + 'T'+ event['end']
    end_date = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S")
    end_date = end_date.replace(tzinfo=local_zone)
    utc_end = end_date.astimezone(utc_zone)
    utc_end = datetime.strftime(utc_end, "%Y-%m-%dT%H:%M:%S-00:00")

    # create event item for attendees
    attendees = []
    for i in event['email']:
        attendees.append({'email': i})
    
    # Event to be added to calendar
    EVENT = {
        'summary':      event['name'],
        # Adding an address into the location field enables features such as 
        # "time to leave" or displaying a map with the directions.
        'location':     event['location'],
        'description':  event['description'],
        #datetime format:'2015-09-15T00:00:00%s' % GMT_OFF
        'start':        {'dateTime': utc_start},
        'end':          {'dateTime': utc_end},
        'attendees':    attendees
    }
    e = service.events().insert(calendarId='primary',
    sendNotifications=True, body=EVENT).execute()

# input is list of emails
def get_incoming_events(mylist, time, service): # use events to find open time slots
    # create custom datetime object from time input
    h, m = time['end'].split(":")
    Y, M, D = time['date'].split("-")
    date = datetime(int(Y), int(M), int(D), int(h), int(m), 0, 0)
    
    # auto-detect local and utc zones
    utc_zone = tz.tzutc()
    local_zone = tz.tzlocal()

    # convert time zone from local to utc
    date = date.replace(tzinfo=local_zone)
    utc_time = date.astimezone(utc_zone)
    now = utc_time.isoformat()[:19] + 'Z' # 'Z' indicates UTC time

    # calendarId is email, in company the calendars are connected
    # error 404: when accessing a calendar that the user can not access
    totallist = []
    results = 10 # max number of events to be returned by api
    
    # get upcoming events for emails in email list
    for email in mylist:
        try:
            events_result = service.events().list(calendarId=email, timeMin=now,
                                                maxResults=results, singleEvents=True,
                                                orderBy='startTime', fields='items(start,end)').execute()
            events = events_result.get('items', [])

            # if not events:
            #     print('No upcoming events found.')
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                date = start[0:10]
                d = {'date': date, 'start': start[11:16], 'end': end[11:16]}
                totallist.append(d)
        
        except: # error handling
            print("User does not have access to target " + email + "'s calendar.")
    
    totallist.sort(key = lambda x: (datetime.strptime(x['date'], '%Y-%m-%d'), datetime.strptime(x['start'], '%H:%M')))
    return totallist

# get current time in dictionary format
def get_now():
    now = datetime.now()
    date = datetime.strftime(now, "%Y-%m-%d")
    end = datetime.strftime(now, "%H:%M")
    d = {'date': date, 'start': "", 'end': end}
    return d

# convert time string to number of minutes
def str_to_min(time_str):
    h, m = time_str.split(':')
    return (int(h) * 60) + int(m)

# convert number of minutes to time string
def min_to_str(time_min):
    m = time_min % 60
    h = int((time_min - m) / 60)
    if h < 10: h_str = "0" + str(h)
    else: h_str = str(h)
    if m < 10: m_str = "0" + str(m)
    else: m_str = str(m)
    return h_str + ":" + m_str 

# find free slot from list of events and group information / input
def find_free_slot(events, start, info):
    e0 = start
    slot_time = info['slot_time']
    offset = info['offset']
    total_time = slot_time + (2 * offset)
    start_of_day = info['start_day']
    end_of_day = info['end_day']
    e_len = len(events)
    i = 0

    # loop through list of ordered events
    while i != e_len:
        e1 = events[i]
        end_min = str_to_min(e0['end'])
        start_min = str_to_min(e1['start'])
        nday = next_day(e0)
        
        # if events occur in the same day
        if same_day(e0, e1):  
            if str_to_min(e0['end']) >= str_to_min(start_of_day):
                if (start_min - end_min >= total_time):
                    time = end_min + offset
                    e0['start'] = min_to_str(time)
                    e0['end'] = min_to_str(time + slot_time)
                    # print("one")
                    return e0
            elif (start_min - str_to_min(start_of_day) >= total_time):
                time = str_to_min(start_of_day) + offset
                e0['start'] = min_to_str(time)
                e0['end'] = min_to_str(time + slot_time)
                # print("two")
                return e0
        # occur on different days
        else:  
            if (str_to_min(end_of_day) - end_min >= total_time):
                if end_min - str_to_min(start_of_day) >= 0:
                    time = end_min + offset
                    e0['start'] = min_to_str(time)
                    e0['end'] = min_to_str(time + slot_time)
                    # print("three")
                    return e0 
                else:
                    time = str_to_min(start_of_day) + offset
                    e0['start'] = min_to_str(time)
                    e0['end'] = min_to_str(time + slot_time)
                    # print("four")
                    return e0
            # if there is a gap of days between events, use day after first event
            elif (nday['date'] != e1['date']):
                time = str_to_min(start_of_day) + offset
                e0['end'] = min_to_str(time + slot_time)
                e0['start'] = min_to_str(time)
                # print("five")
                return e0
            elif (start_min - str_to_min(start_of_day) >= total_time):
                time = str_to_min(start_of_day) + offset
                e1['end'] = min_to_str(time + slot_time)
                e1['start'] = min_to_str(time)
                # print("six")
                return e1
        e0 = e1
        i = i + 1  
    
    # if there are no upcoming events or do not have gaps in events list
    end_min = str_to_min(e0['end'])
    start_min = str_to_min(e0['start'])
    if ((start_min < str_to_min(start_of_day)) and (end_min <= str_to_min(start_of_day))):
        time = str_to_min(start_of_day) + offset
        e0['end'] = min_to_str(time + slot_time)
        e0['start'] = min_to_str(time)
        # print("seven")
    elif (str_to_min(end_of_day) - end_min >= total_time):
        time = end_min + offset
        e0['start'] = min_to_str(time)
        e0['end'] = min_to_str(time + slot_time)
        # print("eight")
    else:
        time = str_to_min(start_of_day) + offset
        e0 = next_day(e0)
        e0['end'] = min_to_str(time + slot_time)
        e0['start'] = min_to_str(time)
        # print("nine")
    return e0

# acquires the date of the next day of the inputted date
def next_day(day):
    nextday = {'date': day['date'], 'start': day['start'], 'end': day['end']} 

    # add one day to datetime object and convert back to string
    date = datetime.strptime(day['date'], "%Y-%m-%d")
    modified_date = date + timedelta(days=1)
    new_date = datetime.strftime(modified_date, "%Y-%m-%d")
    nextday['date'] = new_date 
    return nextday 

# check if two events exist on the same date (not time)
def same_day(e1, e2):
    if (e1['date'] == e2['date']):
        return True
    return False

# use inputs to create information for inserting calendar events
def pairs(name, list_of_lists, time, info, description):
    # get credentials to access api
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)
    
    # default information # need default for description?
    if time is None: time = get_now()
    if info is None: info = {'offset': 10, 'slot_time': 60, 'start_day': '8:00', 'end_day': '20:00', 'location': 'Cornell'}
    if name is None: name = 'Coffee Chat ☕'
    
    # loop through list of pairs
    for i in list_of_lists:
        # get upcoming events in the target pair's calendars
        mylist = get_incoming_events(i, time, service)
        
        # find free slot from list of unavailable time slots
        free_slot = find_free_slot(mylist, time, info)
        location = info['location']

        # append new event to list of events to be inserted into calendar
        # https://www.piliapp.com/twitter-symbols/
        d1 = {'name': name, 'date': free_slot['date'], 'start': free_slot['start'] + ':00', 'end': free_slot['end'] + ':00', 'email': i, 'location': location, 'description': description}
        
        # insert event into calendar
        addevent(d1, service)

if __name__ == '__main__': # For testing
    group = None
    
    # default_time = get_now()
    # starting_time = next_day(default_time)
    starting_time = None
    
    name = None
    
    description = "Have a nice chat with a colleague. You might even make a new friend!"
    description = None
    
    list_of_lists = [["al766@cornell.edu", "al766@cornell.edu"], ["al766@cornell.edu", "al766@cornell.edu"]]
    pairs(name, list_of_lists, starting_time, group, description)