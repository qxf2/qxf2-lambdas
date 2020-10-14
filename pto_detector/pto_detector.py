"""
Get messages for employees from pto-detector SQS
And post to Skype Sender if the message is a PTO message
"""
import boto3
import requests
IS_PTO_URL = 'http://practice-testing-ai-ml.qxf2.com/is-pto'
QUEUE_URL = 'https://sqs.ap-south-1.amazonaws.com/285993504765/skype-sender'

def clean_message(message):
    "Clean up the message received"
    message = message.replace("'", '-')
    message = message.replace('"', '-')

    return message

def get_is_pto(message):
    "Check if the message is a PTO message"
    response = requests.post(url=IS_PTO_URL,data={'message':message})
    result_flag = response.json()['answer'][-20:] == 'is not a PTO message'

    return result_flag

def write_message(daily_message, channel):
    "Send a message to Skype Sender"
    sqs = boto3.client('sqs')
    message = str({'msg':f'{daily_message}', 'channel':channel})
    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=(message))

def lambda_handler(event, context):
    "Lambda entry point"
    print(event)
    message = event.get('msg')
    channel = event.get('chat_id','test')
    is_pto_flag = get_is_pto(clean_message(message))
    if is_pto_flag:
        write_message(message, channel)
