"""
Code level tests for the daily messages lambda
"""
import boto3
import warnings
from unittest import mock
from unittest.mock import patch
from moto import mock_sqs
from daily_messages import daily_messages
import conf.channel_conf as conf

# Added following code to fix deprecation warning
with warnings.catch_warnings():
    warnings.filterwarnings("ignore",category=DeprecationWarning)
    import imp

@mock_sqs
@patch('daily_messages.daily_messages.write_message')
@patch('daily_messages.daily_messages.get_message')
def test_daily_message_lambda_sqs_integration(mock_get_message, mock_write_message):
    "Test the write_message method with a valid message"
    event = {'endpoint':'/message', 'channel':conf.channel}
    sqs = boto3.resource('sqs')
    queue = sqs.create_queue(QueueName='test-skype-sender')
    daily_messages.QUEUE_URL = queue.url
    mock_get_message.return_value = 'Did it mocked really?'
    expected_message = str({'msg':f'Did it mocked really?', 'channel':conf.channel})
    daily_messages.lambda_handler(event=event, context=None)
    sqs_messages = queue.receive_messages()

    # Assertion for get message
    mock_get_message.assert_called_with('/message')
    assert mock_get_message.call_count == 1

    #Asserting for write message
    mock_write_message.assert_called_with('Did it mocked really?', conf.channel)
    assert mock_write_message.call_count == 1
