"""
Get upcoming holidays from Qxf2's holidays page
And post to Skype Sender
"""

from datetime import datetime
import os
import requests
import boto3
from bs4 import BeautifulSoup

QUEUE_URL = os.environ.get('SKYPE_SENDER_QUEUE_URL')
qxf2_holidays = {'optional':{},'public':{}}

def fetch_holidays():
    "Fetch holiday list from holidays webpage"
    now = datetime.now()
    if (now.month ==  12 and now.day == 25):
        url = f'https://qxf2.com/{now.year+1}-holidays.html'
    else:
        url = f'https://qxf2.com/{now.year}-holidays.html'

    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')
    tbody = soup.find("tbody")
    rows = tbody.find_all('tr')

    for row in rows:
        cells = row.find_all("td")
        qxf2_holidays['public'][cells[0].text] = ''.join(cells[2].text.split())

    unordered_list = soup.find_all('ul')
    list_items = unordered_list[5].find_all('li')

    for items in list_items:
        items = items.text.split(',')
        qxf2_holidays['optional'][items[0]] = ''.join(items[2].split())

def get_holidays():
    "Get a holiday message for employees"

    fetch_holidays()
    msg = ''
    today = datetime.today().strftime("%d-%b-%Y")

    for key,value in qxf2_holidays.items():
        for date,name in value.items():
            delta = datetime.strptime(date, "%d-%b-%Y") - datetime.strptime(today, "%d-%b-%Y")
            if key == 'optional':
                end_string = 'Kindly take it if you have not taken one this year. ' \
                            'Mark it on your calendar and inform the client about it.'
            else:
                end_string = 'Kindly inform the client about it right now'

            if delta.days in (7 , 3):
                msg += (f"\n Reminder - {delta.days} days from now {date} is a {name} {key} "
                        f"holiday. {end_string}")
    return msg.replace("'","")

def write_message(holiday_reminder_message, channel):
    "Send a message to Skype Sender"
    # Check if running on localstack or production environment
    is_localstack = os.environ.get('LOCALSTACK_ENV') == 'true'

    if is_localstack:
        sqs = boto3.client('sqs',endpoint_url = 'http://localstack:4566')
    else:
        sqs = boto3.client('sqs')
    print(channel)
    message = str({'msg':f'{holiday_reminder_message}', 'channel':channel})
    print(message)
    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=(message))

def lambda_handler(event, context):
    "lambda entry point"
    message = get_holidays()
    print(message)
    write_message(message, event.get('channel','main'))
    return {
        'msg': message
    }
