"""
Get messages from etc channel, filter urls and post them to newsletter api
"""
import json
import os
import boto3
import requests
import re
from urlextract import URLExtract

def clean_message(message):
    "Clean up the message received"
    message = message.replace("'", '-')
    message = message.replace('"', '-')

    return message

def get_message_contents(event):
    "Retrieve the message contents from the SQS event"
    record = event.get('Records')[0]
    message = record.get('body')
    message = json.loads(message)['Message']
    message = json.loads(message)

    return message

def url_filter(message):
    "Get the message from etc channel and filter only urls"
    extractor = URLExtract()
    url = extractor.find_urls(message)
    print(url)
    print(url[0])

    return (url[0])

def fetch_env_variables():
    "Get the environment variables"
    channel = os.environ.get('ETC_CHANNEL')

    return channel

def lambda_handler(event, context):
    "Lambda processing message from etc and passing url to api for newsletter"
    message_contents = get_message_contents(event)
    message = message_contents['msg']
    channel = message_contents['chat_id']
    user = message_contents['user_id']
    response=""
    filtered_url=""
    '''
    if channel == os.environ.get('QUEUE_URL') and user != os.environ.get('Qxf2Bot_USER'):
    '''
    cleaned_message = clean_message(message)
    filtered_url=url_filter(cleaned_message)
    if filtered_url:
        '''
        response = requests.post('api for newsletter', data = filtered_url)
        '''
        print(response)
    else:
        print("No url found")
