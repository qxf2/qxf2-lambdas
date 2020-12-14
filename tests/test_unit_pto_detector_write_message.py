import os,sys
import boto3
import conf.channel_conf as conf
import warnings
import unittest
from unittest import mock
from moto import mock_sqs
from parameterized import parameterized_class
from pto_detector import pto_detector
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Added following code to fix deprecation warning
with warnings.catch_warnings():
    warnings.filterwarnings("ignore",category=DeprecationWarning)
    import imp

@parameterized_class(("message_to_send", "expected_message"), [
   ('Detected PTO message Test: I am out sick today',str({'msg':f'Detected PTO message Test: I am out sick today', 'channel':conf.channel}),'Detected PTO message Test: I am on PTO tomorrow',str({'msg':f'Detected PTO message Test: I am on PTO tomorrow', 'channel':conf.channel}))])

@mock_sqs
class TestWriteMessage(unittest.TestCase):
    "Declaring class for write method"

    def test_pto_detector_write_message(self):
        """
        Unit test message for write_messsage
        """
        sqs = boto3.resource('sqs')
        queue = sqs.create_queue(QueueName='test-skype-sender')
        pto_detector.QUEUE_URL = queue.url
        pto_detector.write_message(self.message_to_send,conf.channel)
        sqs_message = queue.receive_messages()
        self.assertEqual(sqs_message[0].body,self.expected_message)
        assert len(sqs_message) == 1
