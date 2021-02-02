"""
Lambda helper
"""
import os
import sys
import logging
import boto3
import conf.lambda_configuration_conf as lambda_conf
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def trigger_cron_lambda(lambda_name: str):
    """
    :return: The AWS response.
    Except a response
    """
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    client = boto3.client('lambda')
    Event = {}
    response = client.invoke(FunctionName=lambda_name,InvocationType='Event',\
        LogType='None',Payload=b'{"endpoint": "/message","channel": "test"}')

    return response

def get_request_id_from_lambda_response():
    """
    :return: The request_id
    Except a request_id
    """
    response = trigger_cron_lambda(lambda_conf.daily_message_lambda)
    request_id = response.get('ResponseMetadata')['RequestId']

    return request_id
