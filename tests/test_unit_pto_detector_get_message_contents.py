import os, sys
import boto3
import warnings
from unittest import mock
from unittest.mock import patch
from moto import mock_sqs
from pto_detector import pto_detector
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@mock_sqs
@patch('pto_detector.pto_detector.get_message_contents')
def test_pto_detector_get_message_contents(mock_get_message_contents):
    """
    Unit test for pto_detctor
    """
    event = {
        "Records": [
            {
            "body": "{\"Message\":\"{\\\"msg\\\": \\\"Test: I am out sick today\\\", \\\"chat_id\\\": \\\"19:f33e901e871d4c3c9ebbbbee66e59ebe@thread.skype\\\", \\\"user_id\\\":\\\"blah\\\"}\"}"
            }
        ]
    }

    mock_get_message_contents.return_value =('Test: I am out sick today', 'blah',  '19:f33e901e871d4c3c9ebbbbee66e59ebe@thread.skype')
    expected_message_contents = str({'msg': 'Test: I am out sick today', 'user_id': 'blah', 'chat_id': '19:f33e901e871d4c3c9ebbbbee66e59ebe@thread.skype'})
    pto_detector.get_message_contents(event)
    assert mock_get_message_contents.call_count == 1
    mock_get_message_contents.called_with('Test: I am out sick today', 'blah',  '19:f33e901e871d4c3c9ebbbbee66e59ebe@thread.skype')