"""
This lambda will notify on skype channel about the
unique tech learnt for the current week based on the survey data
"""
from datetime import date,timedelta
import os
import json
import requests
import boto3

QUEUE_URL = os.environ.get('SKYPE_SENDER_QUEUE_URL')
ALL_TECH_URL = os.environ.get('ALL_TECH_URL')
WEEKLY_TECH_URL = os.environ.get('WEEKLY_TECH_URL')
AUTHORIZED_USER = os.environ.get('AUTHORIZED_USER')


def write_message(unique_tech_msg, channel):
    "Send a message to Skype Sender"
    # Check if running on localstack or production environment
    is_localstack = os.environ.get('LOCALSTACK_ENV') == 'true'
    if is_localstack:
        sqs = boto3.client('sqs',endpoint_url = 'http://localstack:4566')
    else:
        sqs = boto3.client('sqs')
    message = str({'msg':f'{unique_tech_msg}', 'channel':channel})
    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=(message))


def get_all_techs():
    "Returns a list of technology data"
    end_date = str(date.today() - timedelta(days=5))
    all_tech = requests.get(ALL_TECH_URL,headers={"Accept":"application/json","User":AUTHORIZED_USER},
                data=json.dumps({"start_date":"2014-01-01","end_date":end_date}))
    tech_list = [tech['technology'] for tech in all_tech.json()]
    return tech_list


def get_weekly_tech():
    "Returns a list of technlogy data for current week"
    todays_date = str(date.today())
    weekly_tech = requests.post(WEEKLY_TECH_URL,data=json.dumps({"date":todays_date}),
                    headers={"Accept":"application/json","Content-type":"application/json","User":AUTHORIZED_USER})
    weekly_tech_list = [tech['Technology'] for tech in weekly_tech.json()]
    return weekly_tech_list


def get_unique_tech():
    "Retun weekly unique tech"
    unique_tech_list =set(get_weekly_tech()) - set(get_all_techs())

    if len(unique_tech_list) != 0:
        msg = "List of unique techs learnt this week:\n"+"\n".join(unique_tech_list)
    else:
        msg = "*No unique techs* learnt this week!! :("
    return msg


def lambda_handler(event, context):
    "Lambda entry point"
    message = get_unique_tech()
    write_message(message, event.get('channel','main'))
    weekly_tech_list = set(get_weekly_tech())
    if len(weekly_tech_list) != 0:
        msg = "List of techs reported this week:\n" + "\n".join(weekly_tech_list)
    else:
        msg = "*No unique techs* learnt this week!! :("
    write_message(msg, event.get('channel','main'))
    return {
        'unique_tech': message,
        'weekly_techs': msg
    }
