"""
Unit tests for write_message method pf pto_detector lambda
"""
import boto3
import conf.channel_conf as conf
import warnings
from moto import mock_sqs
from parameterized import parameterized, parameterized_class
from pto_detector import pto_detector

# Added following code to fix deprecation warning
with warnings.catch_warnings():
    warnings.filterwarnings("ignore",category=DeprecationWarning)
    import imp

def get_class_name(cls, num, params_dict):
    """
    multiple parameters being included in the generated class name:
    """
    return "%s_%s_%s%s" %(
        cls.__name__,
        num,
        parameterized.to_safe_name(params_dict['message_to_send']),
        parameterized.to_safe_name(params_dict['expected_message']),
    )

@parameterized_class([
   { "message_to_send": "Detected PTO message Test: I am out sick today", "expected_message": str({'msg':f'Detected PTO message Test: I am out sick today', 'channel':conf.channel})},
   { "message_to_send": "Detected PTO message Test: I am on PTO today", "expected_message": str({'msg':f'Detected PTO message Test: I am on PTO today', 'channel':conf.channel})},
], class_name_func=get_class_name)

@mock_sqs
class TestWriteMessage(object):
    """
    Declaring class for write method"
    """

    def test_pto_detector_write_message(self):
        """
        Unit test message for write_messsage
        """
        sqs = boto3.resource('sqs')
        queue = sqs.create_queue(QueueName='test-skype-sender')
        pto_detector.QUEUE_URL = queue.url
        pto_detector.write_message(self.message_to_send,conf.channel)
        sqs_message = queue.receive_messages()
        assert sqs_message[0].body == self.expected_message
        assert len(sqs_message) == 1
