"""
This Lambda will :
    - On every friday, lambda will pick up a list of employees who have not filled survey.
    - Reminder will be sent individually to them.
    - At the end of the day, lambda will post employee names who are yet to fill survey.
"""
import os
import json
import boto3
import requests

QUEUE_URL = 'https://sqs.ap-south-1.amazonaws.com/285993504765/skype-sender'
NOT_RESPONDED_USERS_URL = os.environ.get('NOT_RESPONDED_USERS_URL')

def get_all_employees():
    "get all employees data"
    invokelambda = boto3.client('lambda',region_name=os.environ.get('REGION_NAME'))
    response = invokelambda.invoke(FunctionName=os.environ.get('EMPLOYEES_LAMBDA_NAME'),InvocationType="RequestResponse")
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


def get_individual_message():
    "Get message for individual employee"
    emp_data = get_all_employees()
    non_responded_users = get_non_responded_users()
    users = [user['email'] for user in non_responded_users.json()]
    for each_node in emp_data:
            if each_node['node']['email'] in users:
                msg = f"Hey {each_node['node']['firstname']},\nReminder to take Help Survey: {os.environ.get('HELP_SURVEY_URL')}"
                write_message(msg, '8:'+each_node['node']['skypeId'])


def get_group_message():
    "Get group message"
    non_responded_users = get_non_responded_users()
    user_names = [user['fullName'] for user in non_responded_users.json()]
    group_msg = "List of People who have not submitted help survey \n " + \
                "\n" .join(user_names)
    write_message(group_msg, os.environ.get('CHANNEL_ID'))


def survey_reminder(msg_type):
    "Remind Qxf2 employees to take survey"
    if msg_type == 'individual':
        get_individual_message()
    else:
        get_group_message()


def lambda_handler(event, context):
    "lambda entry point"
    survey_reminder(event['msg_type'])
