"""
Get upcoming holidays from Qxf2's holidays page
And post to Skype Sender
"""

import json
import requests
from datetime import datetime 
import boto3
from bs4 import BeautifulSoup

QUEUE_URL = 'https://sqs.ap-south-1.amazonaws.com/285993504765/skype-sender'
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
        
    ul = soup.find_all('ul')
    li = ul[5].find_all('li')
    
    for items in li:
        items = items.text.split(',')
        qxf2_holidays['optional'][items[0]] = ''.join(items[2].split())
    
def get_holidays():
    "Get a holiday message for employees"
    
    fetch_holidays()
    msg = ''
    today = datetime.today().strftime("%d-%b-%Y")
    
    for key,value in qxf2_holidays.items():
        for date,name in qxf2_holidays[key].items():
            delta = datetime.strptime(date, "%d-%b-%Y") - datetime.strptime(today, "%d-%b-%Y") 
            if key == 'optional':
                end_string = 'Kindly take it if you have not taken one this year by marking on calendar and informing client about it'
            else:
                end_string = 'Kindly inform client about it right now'
            
            if delta.days == 7  or delta.days ==3:
                msg += f"\n Reminder - {delta.days} days from now {date} is a {name} {key} holiday. {end_string}"
    return msg.replace("'","")

def write_message(holiday_reminder_message, channel):
    "Send a message to Skype Sender"
    sqs = boto3.client('sqs')
    message = str({'msg':f'{holiday_reminder_message}', 'channel':channel})
    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=(message))

def lambda_handler(event, context):
    "lambda entry point"
    message = get_holidays()
    write_message(message, event.get('channel','main'))

    
    
    

