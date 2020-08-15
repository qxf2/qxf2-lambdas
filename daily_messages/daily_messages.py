"""
Get messages for employees from daily-messages.qxf2.com
And post to Skype Sender
"""
import boto3
import requests
BASE_URL = 'http://daily-messages.qxf2.com'
QUEUE_URL = 'https://sqs.ap-south-1.amazonaws.com/285993504765/skype-sender'
CHANNEL = 'test'

def clean_message(message):
    "Clean up the message received"
    message = message.replace("'",'-')
    message = message.replace('"','-')

    return message

def get_message():
    "Get a message for employees"
    endpoint = '/message'
    response = requests.get(url=BASE_URL+endpoint)

    return clean_message(response.json()['msg'])

def write_message(daily_message):
    "Send a message to Skype Sender"
    sqs = boto3.client('sqs')
    message = str({'msg':f'{daily_message}', 'channel':CHANNEL})
    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=(message))

def employee_daily():
    "Post a message about Qxf2 culture"
    message = get_message()
    write_message(message)
