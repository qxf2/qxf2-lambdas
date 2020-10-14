"""
Get messages for employees from pto-detector SQS
And post to Skype Sender if the message is a PTO message
"""
import json
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

def lambda_handler(event, context):
    "Lambda entry point"
    record = event.get('Records')
    message = record.get('body')
    message = json.loads(message)['Message']
    message = json.loads(message)
    is_pto_flag = get_is_pto(clean_message(message['msg']))
    if is_pto_flag:
        print(f'Detected PTO message {message["msg"]}')
        write_message(message['msg'], message['chat_id'])
