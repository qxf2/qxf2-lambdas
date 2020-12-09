import os, sys
import boto3
import conf.channel_conf as conf
import warnings
from unittest import mock
from unittest.mock import patch
from moto import mock_sqs
from pto_detector import pto_detector
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Added following code to fix deprecation warning
with warnings.catch_warnings():
    warnings.filterwarnings("ignore",category=DeprecationWarning)
    import imp

@mock_sqs
@patch('pto_detector.pto_detector.write_message')
def test_pto_detector_write_message(mock_write_message):
    """
    Unit test message for write_messsage
    """
    mock_write_message.return_value('Detected PTO message Test: I am out sick today')
    expected_message = str({'msg':f'Detected PTO message Test: I am out sick today', 'channel':conf.channel})
    message_to_send = 'Detected PTO message Test: I am out sick today'
    channel = 'test'
    sqs = boto3.resource('sqs')
    queue = sqs.create_queue(QueueName='test-skype-sender')
    pto_detector.QUEUE_URL = queue.url
    pto_detector.write_message(message_to_send,channel)
    sqs_message = queue.receive_messages()
    mock_write_message.called_with('Detected PTO message Test: I am out sick today',conf.channel)
    assert mock_write_message.call_count == 1
