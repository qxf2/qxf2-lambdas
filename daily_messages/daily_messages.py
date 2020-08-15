"""
Get messages for employees from daily-messages.qxf2.com
And post to Skype Sender
"""
import boto3
import requests
BASE_URL = 'http://daily-messages.qxf2.com'
QUEUE_URL = 'https://sqs.ap-south-1.amazonaws.com/285993504765/skype-sender'

def clean_message(message):
    "Clean up the message received"
    message = message.replace("'", '-')
    message = message.replace('"', '-')

    return message

def get_message(endpoint):
    "Get a message for employees"
    response = requests.get(url=BASE_URL+endpoint)

    return clean_message(response.json()['msg'])

def write_message(daily_message, channel):
    "Send a message to Skype Sender"
    sqs = boto3.client('sqs')
    message = str({'msg':f'{daily_message}', 'channel':channel})
    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=(message))

def lambda_handler(event, context):
    "Lambda entry point"
    #This lambda expects an event of type {'endpoint':'/blah','channel':'blah'}
    message = get_message(event.get('endpoint'))
    write_message(message, event.get('channel','test'))
