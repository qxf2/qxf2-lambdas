"""
Lambda to to pull URL from ETC channel messages
"""
import json
import os
import boto3
import requests
import re

EXCLUDE_URL_STRINGS = ['skype.com', 'meet.google.com', 'trello.com/b']

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

def get_url(message):
    "Get the URL from the message"
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url_patterns = re.findall(regex,message)
    urls = []
    for url in url_patterns:
        if url[0][-1] != '-':
            present_flag = False
            for exclude_url in EXCLUDE_URL_STRINGS:
                if exclude_url in url[0]:
                    present_flag = True
                    break
            if not present_flag:
                urls.append(url[0])

    return urls

def post_to_newsletter(final_url, category_id = '2'):
    "Method to call the newsletter API and post the url"

    url = os.environ.get('URL', '')
    headers = {'x-api-key' : os.environ.get('API_KEY_VALUE','')}
    response_status = ""
    if len(final_url) != 0:
        for article_url in final_url:
            data = {'url': article_url, 'category_id': category_id}
            response = requests.post(url, data = data, headers = headers)
            response_status = response.status_code
            print(response_status)
    return response_status          

def lambda_handler(event, context):
    """
    Method run when Lambda is triggered
    calls the filtering logic
    calls the logic to post to endpoint
    """
    content = get_message_contents(event)
    message = content['msg']
    channel = content['chat_id']
    user = content['user_id']
    print(f'{message}, {user}, {channel}')

    response=""
    final_url=[]
    if channel == os.environ.get('ETC_CHANNEL') and user != os.environ.get('Qxf2Bot_USER'):
        print("Getting message posted on ETC ")
        cleaned_message = clean_message(message)
        final_url=get_url(cleaned_message)
        #Filtered URL is printed by lambda
        print("Final url is :",final_url)
        if final_url:
            response = post_to_newsletter(final_url)
        else:
            print("message does not contain any url")
    else:
        print("Message not from ETC channel")

    return {
        'statusCode': response,
        'body': json.dumps(final_url)
    }

