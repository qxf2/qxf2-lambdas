"""
Lambda to to pull URL from ETC channel messages and Assign the article to employee
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

def get_url(message):
    "Get the URL from the message"
    """
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,message)

    return [x[0] for x in url if x[0][-1]!='-']
    """
    extractor = URLExtract()
    urls = extractor.find_urls(message)
    print(urls)
    if urls:
        return (urls[0])
    else: 
        return
    


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
            print ("we got the URL")
        else:
            print("message does not contain any url")
    else:
        print("Message not from ETC channel")

    return {
        'statusCode': response,
        'body': json.dumps(final_url)
    }
