"""
This is a reliability testing to test the impact of sending
tons of messages to the Newsletter automation SQS.
The test covers the following scenarios:
1. Send a batch of messages to the SQS and confirm all the messages are sent
2. Recieve messages from the SQS and make sure all the messages sent earlier are present in the retrieved messages
"""
import os
import boto3
import time
import unittest
import aws_sqs_batchlib

class TestSQS(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.queue_url = os.environ.get('newsletter_queue_url')
        cls.messages = []

    def test_send_batch_messages(self):
        "Send batch messages to the SQS and verify if all messages are sent"

        # Create a list of messages to send
        message_count=50       
        for message in range(message_count):
            self.messages.append({'Id': f'{message}', 'MessageBody': f'https://www.test-qxf2.com/{message}'})
        
        # Send the messages to the queue
        res = aws_sqs_batchlib.send_message_batch(
            QueueUrl=self.queue_url,
            Entries=self.messages,
        )
        assert len(res['Successful']) == message_count        

    def test_receive_messages(self):
        "Retreive messages from the SQS and verify if all the messages sent are retrieved"
        # Receive the messages from the queue
        res = aws_sqs_batchlib.receive_message(
            QueueUrl = self.queue_url,
            MaxNumberOfMessages=100,
            WaitTimeSeconds=15,
        )
               
        # Verify that the messages match the sent messages
        received_messages = {msg['Body'] for msg in res['Messages']}
        for message in self.messages:
            self.assertIn(message['MessageBody'], received_messages, f"Message {message['MessageBody']} should be received")
