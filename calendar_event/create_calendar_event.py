"""
 Lambda to
 - Create an all-day Google Calender event when event title, date and email are provided
"""
import json
import os
from google.oauth2 import service_account
import googleapiclient.discovery
import query_employees as gql

SCOPES = ['https://www.googleapis.com/auth/calendar']
CLIENT_SECRET_FILE = json.loads(os.environ['client_secret_google_calendar'])

def authenticate(email):
    """
    Sets the required credentials to access the Google Calendar API
    Params:
        email : string
    Returns:
        Google Calendar API service object
    Raises:
        Exception for authentication issues if any
    """
    credentials = service_account.Credentials.from_service_account_info(CLIENT_SECRET_FILE,
                                                                            scopes=SCOPES)
    delegated_credentials = credentials.with_subject(email)
    service = googleapiclient.discovery.build('calendar', 'v3',
                    credentials=delegated_credentials, cache_discovery=False)
    return service

def validate_email(emp_email):
    """
    Validates email id against GraphQL service namely, qxf2-employees
    Params:
        emp_email : string
    Returns:
        if valid,
        emp_email : string
    Raises:
        Exception if invalid email
    """
    emails = gql.get_valid_emails()
    if emp_email in emails:
        return emp_email
    else:
        raise Exception('Invalid email!')

def create_event(emp_email, event_title, event_date):
    """
    Creates Google calendar event, as per the details provided in the SQS message body
    Params:
        emp_email : string
        event_title : string
        event_date : string
    Returns:
        None
        prints event link on successful calendar event creation
    Raises:
        Exception if calendar event creation errors out
    """
    service = authenticate(emp_email)
    event = {
    'summary': event_title,
    'start': {
        'date': event_date
    },
    'end': {
        'date': event_date
    },
    'attendees': [
        {'email': emp_email}
    ]
    }
    calendar_event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"Event created: {calendar_event.get('htmlLink')}")
    return calendar_event.get('htmlLink')

def lambda_handler(event, context):
    """
    Lambda entry point
    Params:
        event : dict
        context : dict
    Returns:
        response : dict
    Raises:
        General exceptions
    """
    message = {}
    try:
        email = event['queryStringParameters']['email']
        title = event['queryStringParameters']['title']
        date_of_event = event['queryStringParameters']['date_of_event']
        print(f'\nLambda inputs: {email}, {title}, {date_of_event}\n')
        if email:
            email = validate_email(email)
        if title and date_of_event:
            calendar_link = create_event(email, title, date_of_event)

            message = {
                'message': calendar_link
            }
        else:
            print("Invalid details provided! Please provide valid email, title and date to create calendar event.")
    except Exception as error:
        raise Exception('Experienced issues while creating the Google Calendar event!') from error
    return {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': json.dumps(message)
    }
