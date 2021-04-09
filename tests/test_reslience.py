"""
This is relience testing to test the impact of sending
tones of messages to the listener

"""

import os
import sys
import time
import boto3

sqs = boto3.client('sqs')

def send_messages_to_sqs():
    "Send messages continuously"
    for range (20):
        queue_url = 'value'
        response = sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=10,
        MessageAttributes={
            MessageBody=(
                'Information about current NY Times fiction bestseller for '
                'week of 12/11/2016.'
            )
        )
        print(response['MessageId'])