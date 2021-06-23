"""
This Lambda will :
    - Get a list of Qxf2 employees who have not filled the survey every friday and remind them one more time to fill the survey via skype sender
    - In addition lambda will post a message on skype channel with a list of users who missed filling the survey at eod
"""
import os
import boto3
import json
import requests
from datetime import datetime

QUEUE_URL = 'https://sqs.ap-south-1.amazonaws.com/285993504765/skype-sender'
NOT_RESPONDED_USERS_URL = os.environ.get('NOT_RESPONDED_USERS_URL')

def get_all_employees():
    "get all employees data"
    invokeLambda = boto3.client('lambda',region_name=os.environ.get('REGION_NAME'))
    response = invokeLambda.invoke(FunctionName=os.environ.get('EMPLOYEES_LAMBDA_NAME'),InvocationType="RequestResponse")
    emp_data = json.loads(response['Payload'].read())['body']
    return emp_data
    

def get_non_responded_users():
    "Gets a list of people who have not filled survey"
    response = requests.get(NOT_RESPONDED_USERS_URL, headers={'Accept': 'application/json', 'User': os.environ.get('AUTHORISED_USER')})
    return response


def write_message(survey_reminder_message, channel):
    "Send a message to Skype Sender"
    sqs = boto3.client('sqs')
    message = str({'msg': f'{survey_reminder_message}', 'channel': channel})
    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=(message))


def survey_reminder():
    "Remind Qxf2 employees to take survey"
    emp_data = get_all_employees()
    non_responded_users = get_non_responded_users()
    users = [user['email'] for user in non_responded_users.json()]
    user_names = [user['fullName'] for user in non_responded_users.json()]

    if (datetime.now().strftime("%H") == os.environ.get('HOUR')):
        for each_node in emp_data:
            if each_node['node']['email'] in users:
                msg = f"Hey {each_node['node']['firstname']},\nReminder to take Help Survey: {os.environ.get('HELP_SURVEY_URL')}"
                write_message(msg, '8:'+each_node['node']['skypeId'])
    else:
        group_msg = "List of People who have not submitted help survey \n " + \
                "\n" .join(user_names)
        write_message(group_msg, os.environ.get('CHANNEL_ID'))
        

def lambda_handler(event, context):
    "lambda entry point"
    message = survey_reminder()
