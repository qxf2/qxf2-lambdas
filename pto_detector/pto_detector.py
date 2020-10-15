"""
Get messages for employees from pto-detector SQS
And post to Skype Sender if the message is a PTO message
"""
import json
import os
import boto3
import requests
IS_PTO_URL = 'https://practice-testing-ai-ml.qxf2.com/is-pto'
QUEUE_URL = 'https://sqs.ap-south-1.amazonaws.com/285993504765/skype-sender'

def clean_message(message):
    "Clean up the message received"
    message = message.replace("'", '-')
    message = message.replace('"', '-')

    return message

def get_is_pto(message):
    "Check if the message is a PTO message"
    response = requests.post(url=IS_PTO_URL,data={'message':message})
    result_flag = response.json()['answer'][-16:] == 'is a PTO message'

    return result_flag

def write_message(message, channel):
    "Send a message to Skype Sender"
    sqs = boto3.client('sqs')
    message = str({'msg':f'{message}', 'channel':channel})
    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=(message))

def get_message_contents(event):
    "Retrieve the message contents from the SQS event"
    record = event.get('Records')[0]
    message = record.get('body')
    message = json.loads(message)['Message']
    message = json.loads(message)

    return message

def lambda_handler(event, context):
    "Lambda entry point"
    message_contents = get_message_contents(event)
    message = message_contents['msg']
    channel = message_contents['chat_id']
    user = message_contents['user_id']
    print(f'{message}, {user}, {channel}')
    is_pto_flag = False
    if channel == os.environ.get('PTO_CHANNEL'):
        is_pto_flag = get_is_pto(clean_message(message))
        print(f'{is_pto_flag}')
    if is_pto_flag and user != os.environ.get('Qxf2Bot_USER'):
        message_to_send = f'Detected PTO message {message}'
        write_message(message_to_send, os.environ.get('SEND_CHANNEL'))
