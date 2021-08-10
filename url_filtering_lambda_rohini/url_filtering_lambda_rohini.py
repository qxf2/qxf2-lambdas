"""
Lambda to to pull URL from ETC channel messages
"""
import json
import os
import boto3
import requests
import re

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
    url = re.findall(regex,message)
    return [x[0] for x in url]

def post_to_newsletter(final_url, category_id = '2'):
    "Method to call the newsletter API and post the url"

    url = os.environ.get('URL', '')
    headers = {'x-api-key' : os.environ.get('API_KEY_VALUE','')}
    for article_url in final_url:
        data = {'url': article_url, 'category_id': category_id}
        response = requests.post(url, data = data, headers = headers)
        print(response.status_code)
    return response.status_code

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
    final_url=""
    if channel == os.environ.get('ETC_CHANNEL') and user != os.environ.get('Qxf2Bot_USER'):
        print("Getting message posted on ETC ")
        cleaned_message = clean_message(message)
        final_url=get_url(cleaned_message)
        #Filtered URL is printed by lambda
        print("Final url is :",final_url)
        if final_url:
            #till we get correct endpoint details next line will throw error
            #it worked with my ec2 instance of newsletter which didnt have auth code
            response = post_to_newsletter(final_url)
        else:
            print("message does not contain any url")
    else:
        print("Message not from ETC channel")

    return {
        'statusCode': response,
        'body': json.dumps(final_url)
    }

