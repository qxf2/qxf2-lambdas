"""
Unit test for the methods in pto_detector.py
"""
import os, sys, warnings, requests, boto3
from pto_detector import pto_detector
from unittest import mock
from unittest.mock import patch
from moto import mock_sqs
import tests.conf.channel_configuration_conf as channel_conf

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Added following code to fix deprecation warning
with warnings.catch_warnings():
    warnings.filterwarnings("ignore",category=DeprecationWarning)
    import imp

def test_clean_message():
    "Test to check message get cleaned"
    message = "T'est"
    result = pto_detector.clean_message(message)
    assert result == "T-est"

@patch('requests.post')
def test_get_is_pto_pto_message(mock_post):
    "Test to check message is pto"
    mock_response = mock.Mock()
    mock_post.return_value = mock_response
    mock_response.json.return_value = {'score': 1}
    message = "I am on PTO today"
    result = pto_detector.get_is_pto(message)
    assert result == True

@patch('requests.post')
def test_get_is_pto_non_pto_message(mock_post):
    "Test to check message is non pto"
    mock_response = mock.Mock()
    mock_post.return_value = mock_response
    mock_response.json.return_value = {'score': 0}
    message = "I am happy today"
    result = pto_detector.get_is_pto(message)
    assert result == False

@mock_sqs
def test_write_message():
    "Test to write message"
    sqs = boto3.resource('sqs')
    queue = sqs.create_queue(QueueName='test-skype-sender')
    pto_detector.QUEUE_URL = queue.url
    message = "I am on PTO today"
    channel = channel_conf.channel
    expected_message = str({'msg':f'{message}', 'channel':channel})
    pto_detector.write_message(message,channel)
    sqs_message = queue.receive_messages()

    assert len(sqs_message) == 1
    assert sqs_message[0].body == expected_message

def test_get_message_contents():
    "Test to check get message contents"

    event = {"Records": [{"body": "{\"Message\":\"{\\\"msg\\\": \\\"Test: I am on PTO today\\\", \\\"chat_id\\\": \\\"blah\\\", \\\"user_id\\\":\\\"blah\\\"}\"}"}]}
    expected_message = {'msg': 'Test: I am on PTO today', 'chat_id': 'blah','user_id': 'blah'}

    message = pto_detector.get_message_contents(event)
    assert message == expected_message

    assert message['msg'] == 'Test: I am on PTO today'
