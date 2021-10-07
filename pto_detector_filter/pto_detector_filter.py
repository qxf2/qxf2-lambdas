"""
Get PTO names from the pto detector messages
And post to Skype Sender
"""

from __future__ import print_function
import httplib2
import os
import json
import boto3
import datetime

QUEUE_URL = 'https://sqs.ap-south-1.amazonaws.com/285993504765/skype-sender'

def write_message(daily_message, channel):
    "Send a message to Skype Sender"
    sqs = boto3.client('sqs')
    message = str({'msg':f'{daily_message}', 'channel':channel})
    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=(message))

def lambda_handler(event, context):
    "Lambda entry point"
    pto_list = main()
    print(pto_list)
    message = "No PTO today" if not pto_list else 'PTO today:\n{}'.format("\n".join(pto_list))
    write_message(message, event.get('channel','main'))