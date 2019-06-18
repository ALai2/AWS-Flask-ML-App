# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
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

# https://developers.google.com/calendar/create-events 
# http://wescpy.blogspot.com/2015/09/creating-events-in-google-calendar.html 
# input is a list of dictionaries
# each dictionary represents an event to be added to google calendar
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
            'location': i['location'],
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

# input is list of emails
def get_incoming_events(mylist, time): # use events to find open time slots
    creds = get_credentials()

    service = build('calendar', 'v3', credentials=creds)

    # isoformat = 2019-06-18T13:22:34.425903Z
    now = datetime.utcnow()
    # print(now)

    add_days = 0 # could be positive, negative or zero, need this?
    # utc_offset = 4
    h, m = time['end'].split(":")
    date = datetime(time['year'], time['month'], time['day'], int(h), int(m), 0, 0) # custom date
    
    # auto-detect local and utc zones
    utc_zone = tz.tzutc()
    local_zone = tz.tzlocal()
    date = date.replace(tzinfo=local_zone)
    utc_time = date.astimezone(utc_zone)

    now = (utc_time + timedelta(days=add_days)).isoformat()[:19] + 'Z' # 'Z' indicates UTC time
    # print(now)

    # calendarId is email, in company the calendars are connected
    # error 404: when accessing a calendar that the user can not access
    all_lists = []
    results = 10
    print('Getting the upcoming ' + str(results) + ' events')
    for email in mylist:
        try:
            events_result = service.events().list(calendarId=email, timeMin=now,
                                                maxResults=results, singleEvents=True,
                                                orderBy='startTime').execute()
            events = events_result.get('items', [])

            e_list = []
            if not events:
                print('No upcoming events found.')
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                date = start[0:10]
                y, m, d = date.split('-')
                # 'name': event['summary']
                d = {'year': int(y), 'month': int(m), 'day': int(d), 'start': start[11:16], 'end': end[11:16]}
                e_list.append(d)
            all_lists.append(e_list)
        except:
            print("User does not have access to target " + email + "'s calendar.")
    return all_lists

def get_now():
    now = datetime.now()
    date_str = str(now.year) + "/" + str(now.month) + "/" + str(now.day) + " " + str(now.hour) + ":" + str(now.minute)
    d = {'year': now.year, 'month': now.month, 'day': now.day, 'start': "", 'end': str(now.hour) + ":" + str(now.minute)}
    return d

def str_to_min(time_str):
    h, m = time_str.split(':')
    return (int(h) * 60) + int(m)

def min_to_str(time_min):
    m = time_min % 60
    h = int((time_min - m) / 60)
    if h < 10: h_str = "0" + str(h)
    else: h_str = str(h)
    if m < 10: m_str = "0" + str(m)
    else: m_str = str(m)
    return h_str + ":" + m_str 

# combine and order events in lists
def unavailable_slot(list_of_lists):
    events1 = list_of_lists[0]
    events2 = list_of_lists[1]
    len1 = len(events1)
    len2 = len(events2)
    i = 0
    j = 0
    acc = []
    while (i != len1 or j != len2):
        if i == len1:
            acc.append(events2[j])
            j = j + 1
        elif j == len2:
            acc.append(events1[i])
            i = i + 1
        else:
            e1 = events1[i]
            e2 = events2[j]
            compare = compare_events(e1, e2)
                
            if compare == 0: # equal times
                acc.append(e2)
            elif compare == 1: # (s1, e2)
                e1['end'] = e2['end']
                acc.append(e1)
            elif compare == 2: # (s1, e1)
                acc.append(e1)
            elif compare == 3: # (s2, e1)
                e2['end'] = e1['end']
                acc.append(e2)
            elif compare == 4: # (s2, e2)
                acc.append(e2)
            elif compare == -1:
                acc.append(e1)
                j = j - 1
            else: # compare == -2
                acc.append(e2)
                i = i - 1
            i = i + 1
            j = j + 1
    return acc

def compare_events(event1, event2):
    if event1['year'] < event2['year']: return -1
    elif event1['year'] > event2['year']: return -2
    else:
        if event1['month'] < event2['month']: return -1
        elif event1['month'] > event2['month']: return -2
        else:
            if event1['day'] < event2['day']: return -1
            elif event1['day'] > event2['day']: return -2
            else:
                compare_1 = compare_times(event1['start'], event2['start'])
                compare_2 = compare_times(event1['end'], event2['end'])
                compare_3 = compare_times(event1['start'], event2['end'])
                compare_4 = compare_times(event1['end'], event2['start'])

                if compare_1 == 0 and compare_2 == 0:                       return 0
                # (s1, e2) s1, s2, e1, e2
                elif compare_1 <= 0 and compare_2 <= 0 and compare_4 >= 0:  return 1 
                # (s1, e1) s1, s2, e2, e1
                elif compare_1 <= 0 and compare_2 >= 0:                     return 2 
                # (s2, e1) s2, s1, e2, e1
                elif compare_1 >= 0 and compare_2 >= 0 and compare_3 <= 0:  return 3 
                # (s2, e2) s2, s1, e1, e2
                elif compare_1 >= 0 and compare_2 <= 0:                     return 4 
                # (s1, e1) (s2, e2)
                elif compare_4 <= 0:                                        return -1
                # (s2, e2) (s1, e1)
                # elif compare_3 >= 0:
                else:                                                       return -2
                
def compare_times(time1, time2):
    t1 = str_to_min(time1)
    t2 = str_to_min(time2)
    if t1 < t2: return -1
    elif t1 > t2: return 1
    else: return 0

def find_free_slot(events, start, info):
    e0 = start
    slot_time = info['slot_time']
    offset = info['offset']
    total_time = slot_time + (2 * offset)
    start_of_day = info['start_day']
    end_of_day = info['end_day']
    e_len = len(events)
    i = 0

    while i != e_len:
        e1 = events[i]
        end_min = str_to_min(e0['end'])
        start_min = str_to_min(e1['start'])
        nday = next_day(e0)
        
        if same_day(e0, e1):  
            if str_to_min(e0['end']) > str_to_min(start_of_day):
                if (start_min - end_min > total_time):
                    time = end_min + offset
                    e0['start'] = min_to_str(time)
                    e0['end'] = min_to_str(time + slot_time)
                    return e0
            elif (start_min - str_to_min(start_of_day) > total_time):
                time = str_to_min(start_of_day) + offset
                e0['start'] = min_to_str(time)
                e0['end'] = min_to_str(time + slot_time)
                return e0
        
        else:  
            if (str_to_min(end_of_day) - end_min > total_time):
                if end_min - str_to_min(start_of_day) > 0:
                    time = end_min + offset
                    e0['start'] = min_to_str(time)
                    e0['end'] = min_to_str(time + slot_time)
                    return e0 
                else:
                    time = str_to_min(start_of_day) + offset
                    e0['start'] = min_to_str(time)
                    e0['end'] = min_to_str(time + slot_time)
                    return e0
            elif (not (nday['year'] == e1['year'] and nday['month'] == e1['month'] and nday['day'] == e1['day'])):
                time = str_to_min(start_of_day) + offset
                e0['end'] = min_to_str(time + slot_time)
                e0['start'] = min_to_str(time)
                return e0
            elif (start_min - str_to_min(start_of_day) > total_time):
                time = str_to_min(start_of_day) + offset
                e1['end'] = min_to_str(time + slot_time)
                e1['start'] = min_to_str(time)
                return e1
        
        e0 = e1
        i = i + 1  
    
    end_min = str_to_min(e0['end'])
    if (str_to_min(end_of_day) - end_min > total_time):
        time = end_min + offset
        e0['start'] = min_to_str(time)
        e0['end'] = min_to_str(time + slot_time)
    else:
        time = str_to_min(start_of_day) + offset
        e0 = next_day(e0)
        e0['end'] = min_to_str(time + slot_time)
        e0['start'] = min_to_str(time)
    return e0

def next_day(day):
    nextday = {'year': day['year'], 'month': day['month'], 'day': day['day'], 'start': day['start'], 'end': day['end']}
    s = str(nextday['year']) + "/" + str(nextday['month']) + "/" + str(nextday['day'])
    
    date = datetime.strptime(s, "%Y/%m/%d")
    modified_date = date + timedelta(days=1)
    new_date = datetime.strftime(modified_date, "%Y/%m/%d")
    
    y, m, d = new_date.split("/")
    nextday['year'] = int(y)
    nextday['month'] = int(m)
    nextday['day'] = int(d)
    return nextday 

def same_day(e1, e2):
    if (e1['year'] == e2['year'] and 
        e1['month'] == e2['month'] and 
            e1['day'] == e2['day']):
                return True 
    return False

# call pairs method in api?
def pairs(list_of_pairs, starting_time, group):
    # groups, offset, slot_time, start_day, end_day, location
    # if no group info set to default
    # have custom starting datetime instead of using current time?
    # default is current time
    if starting_time is not None: time = starting_time 
    else: time = get_now()
    
    if group is not None: info = group 
    else: info = {'offset': 10, 'slot_time': 60, 'start_day': '8:00', 'end_day': '20:00', 'location': 'Cornell'}
    
    for (email1, email2) in list_of_pairs:
        all_lists = get_incoming_events([email1, email2], time)
        mylist = unavailable_slot(all_lists)

        free_slot = find_free_slot(mylist, time, info)

        location = info['location']
        return free_slot
        
        # insert event to calendar with email1 and email2 as accomplices, and also location of meeting
        # mylist = []
        # use free slot and location info to create event info
        
        # if (free_slot['month'] < 10): month = "0" + str(free_slot['month'])
        # else: month = str(free_slot['month'])
        # if (free_slot['day'] < 10): month = "0" + str(free_slot['day'])
        # else: day = str(free_slot['day'])
        # date = str(free_slot['year']) + "-" + month + "-" + day

        # d1 = {'name': 'Friendly Coffee Chat', 'date': date, 'start': free_slot['start'] + ':00', 'end': free_slot['end'] + ':00', 'email1': email1, 'email2': email2, 'location': location}
        # mylist.append(d1)
        # addevent(mylist)

if __name__ == '__main__': # For testing
    info = {'offset': 10, 'slot_time': 60, 'start_day': '8:00', 'end_day': '20:00', 'location': 'Cornell'}

    # mylist = []
    # d1 = {'name': 'Testing', 'date': '2019-06-18', 'start': '11:00:00', 'end': '12:00:00', 'email1': 'al766@cornell.edu', 'email2': 'al766@cornell.edu', 'location': location}
    # d2 = {'name': 'Testing', 'date': '2019-06-17', 'start': '15:00:00', 'end': '17:00:00', 'email1': 'al766@cornell.edu', 'email2': 'al766@cornell.edu', 'location': location}
    # mylist.append(d1)
    # mylist.append(d2)
    # addevent(mylist)
    
    default_time = get_now()
    get_incoming_events(["al766@cornell.edu"], default_time)
    # print("\nCurrent Time: " + json.dumps(get_now()))
    
    # events1 = []
    # events2 = []
    # d1 = {'year': 2019, 'month': 6, 'day': 18, 'start': "8:00", 'end': "22:00"}
    # d2 = {'year': 2019, 'month': 6, 'day': 19, 'start': "6:00", 'end': "18:00"}
    # d3 = {'year': 2019, 'month': 6, 'day': 19, 'start': "20:00", 'end': "23:00"}
    # d4 = {'year': 2019, 'month': 6, 'day': 21, 'start': "8:00", 'end': "22:00"}
    
    # events1.append(d1)
    # events2.append(d2)
    # events1.append(d3)
    # events2.append(d4)
    # mylist = unavailable_slot([events1, events2])
    # print(json.dumps(mylist))
    # print("\n" + json.dumps(find_free_slot(mylist, default_time, info)))