"""
Helper module for sqs messages
"""
import os
import sys
import boto3
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_sqs_client():
    """
    Return sqs_client object
    :param none
    :return sqs_client
    """
    sqs_client = boto3.client('sqs')

    return sqs_client

def get_sqs_queue(queue_url):
    """
    Return queue object from queue_url
    :param queue_url
    :return queue
    """
    queue = boto3.resource('sqs').get_queue_by_name(QueueName=queue_url)

    return queue

def get_message_from_queue(queue_url):
    """
    get messsage from queue_url
    """
    sqs_client = get_sqs_client()
    queue = get_sqs_queue(queue_url)
    message = sqs_client.receive_message(QueueUrl=queue.url)

    return message

def purge_sqs_queue(queue_url):
    """
    Reteun status
    """
    queue = get_sqs_queue(queue_url)
    client = get_sqs_client()
    client.purge_queue(QueueUrl=queue.url)
