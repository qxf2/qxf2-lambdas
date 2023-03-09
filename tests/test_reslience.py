"""
This is a reliability testing to test the impact of sending
tons of messages to the listener.
"""

import os
import sys
import time
import boto3

sqs = boto3.client('sqs')
newsletter_queue_url = os.environ.get('newsletter_queue_url')

def test_send_messages_to_sqs():
    """Send messages continuously"""
    response_messages = []
    message_count = 20
    for count in range(message_count):
        response = sqs.send_message(
            QueueUrl=newsletter_queue_url,
            DelaySeconds=10,
            MessageBody=(
                'Information about current NY Times fiction bestseller for '
                'week of 12/11/2016.'
            ),
        )
        #print(response['MessageId'])
        response_messages.append(response['MessageId'])

    assert len(response_messages) == message_count
