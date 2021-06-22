"""
This lambda will notify on skype channel about the unique tech learnt for the current week based on the survey data
"""
import os
import json
import requests
import boto3
from datetime import date

QUEUE_URL = 'https://sqs.ap-south-1.amazonaws.com/285993504765/skype-sender'
ALL_TECH_URL = os.environ.get('ALL_TECH_URL')
WEEKLY_TECH_URL = os.environ.get('WEEKLY_TECH_URL')
AUTHORIZED_USER = os.environ.get('AUTHORIZED_USER')


def write_message(unique_tech_msg, channel):
    "Send a message to Skype Sender"
    sqs = boto3.client('sqs')
    message = str({'msg':f'{unique_tech_msg}', 'channel':channel})
    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=(message))


def get_all_techs():
    "Returns a list of technology data"
    all_tech = requests.get(ALL_TECH_URL,headers={"Accept":"application/json","User":AUTHORIZED_USER})
    tech_list = [tech['technology'] for tech in all_tech.json()]
    return tech_list


def get_weekly_tech():
    "Returns a list of technlogy data for current week"
    todays_date = str(date.today())
    weekly_tech = requests.post(WEEKLY_TECH_URL,data=json.dumps({"date":todays_date}),headers={"Accept":"application/json","Content-type":"application/json","User":AUTHORIZED_USER})
    weekly_tech_list = [tech['Technology'] for tech in weekly_tech.json()]
    return weekly_tech_list


def get_unique_tech():
    "Retun weekly unique tech"
    unique_tech_list =list(set(get_weekly_tech()) - set(get_all_techs()))
    if len(unique_tech_list) != 0:
        msg = "List of unique techs learnt this week:\n"+"\n".join(unique_tech_list)
    else:
        msg = "*No unique techs* learnt this week!! :("
    return msg


def lambda_handler(event, context):
    "lambda entry point"
    message = get_unique_tech()
    write_message(message, event.get('channel','test'))
