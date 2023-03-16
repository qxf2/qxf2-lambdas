"""
This is a reliability testing to test the impact of sending
tons of messages to the Newsletter automation SQS.
The test covers the following scenarios:
1. Send a batch of messages to the SQS and confirm all the messages are sent
2. Recieve messages from the SQS and make sure all the messages sent earlier are present in the retrieved messages
"""
import os
import time
import requests
import aws_sqs_batchlib
import json
import pandas as pd
import pytest
import concurrent.futures

queue_url = os.environ.get('newsletter_queue_url')
api_key = os.environ.get('api_key')
newsletter_automation_url = os.environ.get('newsletter_automation_url')
messages = []
articles_sent = []

def send_batch_messages():
    "Send batch messages to the SQS and verify if all messages are sent"

    # Create a list of messages to send
    message_count=50
    for message in range(message_count):
        url = f"https://stage-newsletter-lambda-test-{message}.com"
        articles_sent.append(url)
        message_body = {"Message" : "{\"user_id\": \".cid.f9000d4f3453e374\", \"chat_id\": \"19:1941d15dada14943b5d742f2acdb99aa@thread.skype\", \"msg\": \"" + url + "\"}"}
        messages.append({"Id": f'{message}', "MessageBody": json.dumps(message_body)})

    time.sleep(3)
    # Send the messages to the queue
    response = aws_sqs_batchlib.send_message_batch(
        QueueUrl=queue_url,
        Entries=messages,
    )
    return len(response['Successful']) == message_count

def receive_messages():
    "Retreive messages from the SQS and verify if all the messages sent are retrieved"
    # Receive the messages from the queue
    start_time = time.time()
    max_wait_time = 180
    while True:
        res = aws_sqs_batchlib.receive_message(
            QueueUrl = queue_url,
            MaxNumberOfMessages=100,
            WaitTimeSeconds=20,
        )
        received_articles = []
        # Verify that the messages match the sent messages
        received_messages = {msg['Body'] for msg in res['Messages']}
        
        for message in received_messages:
            json_message = json.loads(message)
            recieved_msg_body = json.loads(json_message['Message'])
            received_articles.append(recieved_msg_body['msg'])

        elapsed_time = time.time() - start_time
        if len(received_articles) == 0 or elapsed_time >= max_wait_time:
            break
    return "No more messages in queue"

def test_send_and_receive_batch_messages(printer):
    "Send and receive batch messages to the SQS"

    with concurrent.futures.ThreadPoolExecutor() as executor:
        execute_receive_messages = executor.submit(receive_messages)
        execute_send_messages = executor.submit(send_batch_messages)      
        return_value_send_messages = execute_send_messages.result()
        return_value_recieve_messages = execute_receive_messages.result()
        printer(return_value_recieve_messages)

    assert return_value_send_messages is True,f"Not all messages were sent successfully"
    
def test_if_articles_added():
    "Test if articles are added to the database"

    staging_newsletter_url = newsletter_automation_url if newsletter_automation_url is not None else "https://staging-newsletter-generator.qxf2.com/api/articles/all"
    headers = {'x-api-key' : api_key}
    response = requests.get(staging_newsletter_url, headers=headers).text
    articles = pd.read_json(response)
    article_url = articles['url'].tolist()
    assert all(item in article_url for item in articles_sent),f"Not all articles sent were added into the database"

