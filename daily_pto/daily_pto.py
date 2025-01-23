"""
Get PTO names from the google calender and post them to Skype Sender.
This script uses the Google Calendar API to fetch PTO events 
from shared calendars and posts the names of individuals on PTO to a Skype channel via AWS SQS.
Prerequisite:
- Set environment variables for SERVICE_ACCOUNT_CREDENTIALS, DELEGATED_EMAIL and MAIN_CHANNEL
"""

import os
import json
import datetime
import boto3
from google.oauth2 import service_account
import googleapiclient.discovery

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/client_secret_google_calendar.json
READONLY_CALENDAR_SCOPE = ['https://www.googleapis.com/auth/calendar.readonly']
SERVICE_ACCOUNT_CREDENTIALS = json.loads(os.environ['client_secret_google_calendar'])
QUEUE_URL = 'https://sqs.ap-south-1.amazonaws.com/285993504765/skype-sender'
DELEGATED_EMAIL = os.environ.get('DELEGATED_EMAIL')

def fetch_pto_names():
    """
    Fetches and returns a list of PTO names for today from Google Calendar.
    Authenticates via service account, retrieves calendar IDs, and filters PTO event.
    """
    credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_CREDENTIALS, scopes=READONLY_CALENDAR_SCOPE
        )
    delegated_credentials = credentials.with_subject(DELEGATED_EMAIL)
    service = googleapiclient.discovery.build(
        'calendar', 'v3', credentials=delegated_credentials, cache_discovery=False
        )

    # Fetch calendar IDs shared/subscribed with the test qxf2 user
    # Src: https://developers.google.com/google-apps/calendar/v3/reference/calendarList/list
    page_token = None
    shared_calendar_ids = []
    pto_names_list = []
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            if '@qxf2.com' in calendar_list_entry['id']:
                shared_calendar_ids.append(calendar_list_entry['id'])
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    # Fetch the PTO events for today from each calendar and filter out PTO events
    # Src: https://developers.google.com/google-apps/calendar/v3/reference/events/list
    now = datetime.datetime.now()
    year = int (now.strftime("%Y"))
    month = int (now.strftime("%m"))
    date = int (now.strftime("%d"))
    start_date = datetime.datetime.now().replace(microsecond=0).isoformat() + 'Z'
    today = start_date.split("T")[0]
    end_date = datetime.datetime(year,month,date, 23, 59, 59, 0).isoformat() + 'Z'
    for calendar_id in shared_calendar_ids:
        eventsResult = service.events().list(
            calendarId=calendar_id,
            timeMin=start_date,
            timeMax=end_date,
            singleEvents=True,
            orderBy='startTime').execute()
        events = eventsResult.get('items', [])

        for event in events:
            if 'summary' in event:
                if 'PTO' in event['summary']:
                    if today in event['start']['date']:
                        organizer_name = event['organizer']['email'].split("@")[0]
                        pto_names_list.append(organizer_name)
    return pto_names_list

def write_message(daily_message, channel):
    "Send a message to Skype Sender"
    sqs = boto3.client('sqs')
    message = str({'msg':f'{daily_message}', 'channel':channel})
    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=(message))

def lambda_handler(event, context):
    "Lambda entry point"
    pto_list = fetch_pto_names()
    if pto_list:
        message = 'PTO today:\n{}'.format("\n".join(pto_list))
    else:
        message = 'No PTO today.'
    MAIN_CHANNEL = os.environ.get('MAIN_CHANNEL')
    write_message(message, event.get('channel', MAIN_CHANNEL))