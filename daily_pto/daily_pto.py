"""
Get PTO names from the google calender and post them to Skype Sender.
This script uses the Google Calendar API to fetch PTO events 
from shared calendars and posts the names of individuals on PTO to a Skype channel via AWS SQS.
"""

from __future__ import print_function
import os
import json
import datetime
import boto3
from google.oauth2 import service_account
import googleapiclient.discovery

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/client_secret_google_calendar.json
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CLIENT_SECRET_FILE = json.loads(os.environ['client_secret_google_calendar'])
QUEUE_URL = 'https://sqs.ap-south-1.amazonaws.com/285993504765/skype-sender'

def main():
    """
    Fetches and returns a list of PTO names for today from Google Calendar.
    Authenticates via service account, retrieves calendar IDs, and filters PTO events.
    """
    credentials = service_account.Credentials.from_service_account_info(CLIENT_SECRET_FILE,
                                                                        scopes=SCOPES)
    delegated_credentials = credentials.with_subject('test@qxf2.com')
    service = googleapiclient.discovery.build('calendar', 'v3',
                                              credentials=delegated_credentials,
                                              cache_discovery=False)

    # Fetch calendar IDs shared/subscribed with the test qxf2 user
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

    # Fetch the PTO events for today from each calendar and filter out PTO events
    # Src: https://developers.google.com/google-apps/calendar/v3/reference/events/list
    now = datetime.datetime.now()
    year = int (now.strftime("%Y"))
    month = int (now.strftime("%m"))
    date = int (now.strftime("%d"))
    start_date = datetime.datetime.now().replace(microsecond=0).isoformat() + 'Z'
    today = start_date.split("T")[0]
    end_date = datetime.datetime(year,month,date, 23, 59, 59, 0).isoformat() + 'Z'
    for calendar_id in calendar_ids:
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
                        pto_name = event['organizer']['email'].split("@")[0]
                        pto_list.append(pto_name)
    return pto_list

def write_message(daily_message, channel):
    "Send a message to Skype Sender"
    sqs = boto3.client('sqs')
    message = str({'msg':f'{daily_message}', 'channel':channel})
    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=(message))

def lambda_handler(event, context):
    "Lambda entry point"
    pto_list = main()
    if pto_list:
        message = 'PTO today:\n{}'.format("\n".join(pto_list))
    else:
        message = "No PTO's today."
    channel = event.get('channel', os.environ.get('MAIN_CHANNEL'))
    write_message(message, channel)