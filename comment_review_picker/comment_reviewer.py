"""
This Lambda will :
   - Give a list of comment reviewers
"""
import json
import os
import boto3
import re
import random
QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/285993504765/skype-sender'


def write_message(message, channel):
    "Send a message to Skype Sender"
    sqs = boto3.client('sqs')
    print(channel)
    message = str({'msg':f'{message}', 'channel':channel})
    print(message)
    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=(message))

def select_comment_reviewer():
    "Fetch the list of comment_reviewers from environment variable"
    comment_reviewers = os.environ.get('comment_reviewers','')
    return comment_reviewers

def get_comment_reviewer(comment_reviewers):
    "Return a list of comment reviewers"
    return os.environ.get(comment_reviewers,"").split(',')
    
def pick_random_user(comment_reviewers_list):
    "Pick a raandom employee to review the comment"
    tmp = comment_reviewers_list[:]
    result = [tmp.pop(random.randrange(len(tmp))) for _ in range(1)]
    listToStr = ' '.join(map(str, result))
    return listToStr

def get_reply(message_contents):
    "Create a message to post the comment_reviewer on skype"
    comment_reviewers_list = get_comment_reviewer('comment_reviewers')
    comment_reviewer = pick_random_user(comment_reviewers_list)
    reply = f'A new comment has been posted on our blog {message_contents} .Comment Reviewer: {comment_reviewer}'
    
    return reply


def lambda_handler(event, context):
    "Comment reviewer lambda"
    message_contents = event['comment_link']
    print(message_contents)
    comment_reviewer=get_reply(message_contents)
    print(comment_reviewer)
    channel = os.environ.get('channel','')
    write_message(comment_reviewer, channel)

    return {
        'statusCode': 200,
        'body': json.dumps('Done!')
    }