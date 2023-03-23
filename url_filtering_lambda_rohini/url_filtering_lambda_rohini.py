"""
Lambda to to pull URL from ETC channel messages
"""
import json
import os
import re
import random
import boto3
import requests
import validators

EXCLUDE_URL_STRINGS = ['skype.com', 'meet.google.com', 'trello.com/b']
QUEUE_URL = 'https://sqs.ap-south-1.amazonaws.com/285993504765/skype-sender'


def clean_message(message):
    "Clean up the message received"
    message = message.replace("'", '-')
    message = message.replace('"', '-')

    return message

def get_message_contents(event):
    "Retrieve the message contents from the SQS event"
    print(event)
    print(event.get('Records'))
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
            if not present_flag and validators.url(url[0]):
                urls.append(url[0])

    return urls

def post_to_newsletter(final_url, article_editor, category_id = '5'):
    "Method to call the newsletter API and post the url"
    url = os.environ.get('URL', '')
    category_id = os.environ.get('DEFAULT_CATEGORY', category_id)
    headers = {'x-api-key' : os.environ.get('API_KEY_VALUE','')}
    response_status = ""
    if len(final_url) != 0:
        for article_url in final_url:
            data = {'url': article_url, 'category_id': category_id, 'article_editor': article_editor}
            response = requests.post(url, data = data, headers = headers)
            response_status = response.status_code
            print(response_status)
    return response_status          

def pick_random_user(article_editors_list):
    "Return a random employee to edit the article"
    tmp = article_editors_list[:]
    result = [tmp.pop(random.randrange(len(tmp))) for _ in range(1)]
    listToStr = ' '.join(map(str, result))

    return listToStr

def get_article_editor(employee_list):
    "Return a list of primary comment reviewers"
    return os.environ.get(employee_list,"").split(',')

def write_message(message, channel):
    "Send a message to Skype Sender"
    sqs = boto3.client('sqs')
    print(channel)
    message = str({'msg':f'{message}', 'channel':channel})
    print(message)
    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=(message))

def get_reply():
    "Get the Employee to edit the article for newsletter"
    article_editors_list = get_article_editor('employee_list')
    article_editor = pick_random_user(article_editors_list)
    reply = f'Article editor: {article_editor}'

    return reply,article_editor

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
            reply,article_editor = get_reply()
            response = post_to_newsletter(final_url, article_editor)
            write_message(reply, os.environ.get('ETC_CHANNEL',''))
        else:
            print("message does not contain any url")
    else:
        print("Message not from ETC channel")

    return {
        'statusCode': response,
        'body': json.dumps(final_url)
    }
