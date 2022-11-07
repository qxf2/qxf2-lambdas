"""
Get messages for employees from pto-detector SQS
And post to Skype Sender if the message is a PTO message
"""
from calendar import calendar
import json
import os
import boto3
import requests
IS_PTO_URL = 'https://practice-testing-ai-ml.qxf2.com/is-pto'
QUEUE_URL = 'https://sqs.ap-south-1.amazonaws.com/285993504765/skype-sender'
CALENDAR_EVENT_LAMBDA = os.environ.get('CALENDAR_EVENT_LAMBDA')
EVENT_CLASSIFIER_LAMBDA = os.environ.get('EVENT_CLASSIFIER_LAMBDA')

def clean_message(message):
    "Clean up the message received"
    message = message.replace("'", '-')
    message = message.replace('"', '-')

    return message

def get_is_pto(message):
    "Check if the message is a PTO message"
    response = requests.post(url=IS_PTO_URL,data={'message':message})
    result_flag = response.json()['score'] == 1

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

def invoke_lambda(lambda_func,type,payload='{}'):
    'to invoke aws lambda'
    lambdaClient = boto3.client('lambda')
    response = lambdaClient.invoke(FunctionName=lambda_func, 
                        InvocationType=type,
                        Payload=payload
                        ) 
    return response

def lambda_handler(event, context):
    "Lambda entry point"
    message_contents = get_message_contents(event)
    message = message_contents['msg']
    channel = message_contents['chat_id']
    user = message_contents['user_id']
    print(f'{message}, {user}, {channel}')
    is_pto_flag = False
    if channel == os.environ.get('PTO_CHANNEL') and user != os.environ.get('Qxf2Bot_USER'):
        cleaned_message = clean_message(message)
        is_pto_flag = get_is_pto(cleaned_message)
        print(f'{is_pto_flag}')
    if is_pto_flag and user != os.environ.get('Qxf2Bot_USER'):
        message_to_send = f'Detected PTO message {cleaned_message}'
        write_message(message_to_send, os.environ.get('SEND_CHANNEL'))
    if is_pto_flag == True:
        invoke_type = 'RequestResponse'
        try:
            classifier_response = invoke_lambda(EVENT_CLASSIFIER_LAMBDA,invoke_type,message)
            classifier_payload = json.loads(classifier_response['Payload'].read())
            if classifier_payload.get('statusCode')==200:
                pto_date = classifier_payload.get('body')
                write_message(f'Detected PTO dates are {pto_date}', os.environ.get('SEND_CHANNEL'))
                calendar_event_response = invoke_lambda(CALENDAR_EVENT_LAMBDA,invoke_type,pto_date)
                calendar_event_payload = json.loads(calendar_event_response['Payload'].read())
                if calendar_event_payload.get('statusCode')==200 and if calendar_event_payload.get('body') == "calendar event created":
                   write_message(f'calendar event successfully created', os.environ.get('SEND_CHANNEL'))               
        except Exception as error:
            print(error)
            raise Exception('Experiencing issues with Event Classifier Lambda / Calendar Event Lambda') from error