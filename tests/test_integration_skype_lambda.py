"""
Code level tests for the skype sender lambda
"""
import os
import sys
import boto3
from unittest import mock
from unittest.mock import patch
from skype_sender import qxf2_skype_sender
import tests.conf.channel_configuration_conf as channel_conf
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@patch('skype_sender.qxf2_skype_sender.post_message')
def test_skype_sender_lambda(mock_post_message):
    "Test to write post messages"
    event = {"Records": [{"body": "{'msg': '<b>Test message</b> I am a test message from lambda-tester', 'channel':channel_conf.channel}"}]}
    mock_post_message.return_value = '<b>Test message</b> I am a test message from lambda-tester'

    # Triggering the response
    qxf2_skype_sender.post_message(event=event,context=None)

    #Assertion
    mock_post_message.assert_called_with(event=event,context=None,)
    assert mock_post_message.call_count == 1
