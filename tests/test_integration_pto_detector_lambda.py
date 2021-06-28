"""
Integration test for pto detector lambda

"""
import os
import sys
import boto3
import ast
import collections
import warnings
from unittest import mock
from unittest.mock import patch
from moto import mock_sqs
from pto_detector import pto_detector
import tests.conf.channel_configuration_conf as channel_conf
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Added following code to fix deprecation warning
with warnings.catch_warnings():
    warnings.filterwarnings("ignore",category=DeprecationWarning)
    import imp

@mock_sqs
@patch('pto_detector.pto_detector.write_message')
@patch('pto_detector.pto_detector.clean_message')
@patch('pto_detector.pto_detector.get_message_contents')
def test_integration_pto_detector_lambda(mock_get_message_contents,mock_clean_message,mock_write_message):
    "Integration test for pto detector lambda"
    event = {"Records": [{"body": "{\"Message\":\"{\\\"msg\\\": \\\"Test: I am out sick today\\\", \\\"chat_id\\\": \\\"blah\\\", \\\"user_id\\\":\\\"blah\\\"}\"}"}]}
    sqs = boto3.resource('sqs')
    queue = sqs.create_queue(QueueName='test-skype-sender')
    pto_detector.QUEUE_URL = queue.url
    mock_get_message_contents.return_value = {'msg': 'Test: I am out sick today', 'chat_id': 'blah','user_id': 'blah'}
    mock_clean_message.return_value = 'Test: I am out sick today'
    expected_message = str({'msg':'Detected PTO message Test: I am out sick today', 'channel':channel_conf.channel})
    mock_write_message.return_value = expected_message
    pto_detector.lambda_handler(event=event,context=None)
    sqs_message = queue.receive_messages()

    #asserting get message
    assert mock_get_message_contents.call_count == 1
    mock_get_message_contents.assert_called_with(event)
