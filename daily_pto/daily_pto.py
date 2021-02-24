from __future__ import print_function
import httplib2
import os
import json
import datetime
# from datetime import timedelta
import googleapiclient.discovery as discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
 
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
 
# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret_google_calendar.json'
APPLICATION_NAME = 'Quickstart'
 
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
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials
 

def main():
    """Shows basic usage of the Google Calendar API.
 
    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

 # This code is to fetch the calendar ids shared with me
    # Src: https://developers.google.com/google-apps/calendar/v3/reference/calendarList/list
    page_token = None
    calendar_ids = []
    pto_list = []
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            if '@qxf2.com' in calendar_list_entry['id']:
                calendar_ids.append(calendar_list_entry['id'])
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break
 
    # This code is to look for all-day events in each calendar for the month
    # Src: https://developers.google.com/google-apps/calendar/v3/reference/events/list
    # You need to get this from command line
    now = datetime.datetime.now() # current date and time
    year = int (now.strftime("%Y"))
    month = int (now.strftime("%m"))
    date = int (now.strftime("%d"))
    start_date = datetime.datetime.now().replace(microsecond=0).isoformat() + 'Z'
    today = start_date.split("T")[0]
    end_date = datetime.datetime(year,month,date, 23, 59, 59, 0).isoformat() + 'Z'
    print("Today's PTO List:")
    for calendar_id in calendar_ids:
        count = 0
        eventsResult = service.events().list(
            calendarId=calendar_id,
            timeMin=start_date,
            timeMax=end_date,
            singleEvents=True,
            orderBy='startTime').execute()
        events = eventsResult.get('items', [])

        for event in events:
            if event.__contains__('summary'):
                if 'PTO' in event['summary']:
                    if today in event['start']['date']:
                        count += 1 
                        pto_name = event['creator']['email'].split("@")[0]
                        pto_list.append(pto_name)
                        print(pto_list)

    return pto_list


def write_message(daily_message, channel):
    "Send a message to Skype Sender"
    sqs = boto3.client('sqs')
    message = str({'msg':f'{daily_message}', 'channel':channel})
    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=(message))

def lambda_handler(event, context):
    "Lambda entry point"
    pto_list = main() 
    for msg in pto_list:
        message = '{}Is on PTO'.format(msg)
        write_message(message, event.get('channel','test'))
