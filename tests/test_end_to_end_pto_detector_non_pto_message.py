"""
This End to end test employee skype message covers following:
Step 1: Trigger non pto detector message from pto detector lambda
Step 2: Validate if that message has score on in it.

"""

import os
import sys
import time
import asyncio
from datetime import datetime, timedelta
import json
import logging
import boto3
import pytest
import unittest
import tests.helpers.cloudwatch_helper
import tests.conf.cloudwatch_configuration_conf as cloudwatch_conf
from pythonjsonlogger import jsonlogger
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# logging
log_handler = logging.StreamHandler()
log_handler.setFormatter(jsonlogger.JsonFormatter())
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

class ptodetectortest():
  """
  class for pto detector test
  """
  def trigger_cron_lambda(self,lambda_name: str):
      """
      :return: The AWS response.
      Except a response
      """
      _logger = logging.getLogger(__name__)
      _logger.setLevel(logging.DEBUG)
      client = boto3.client('lambda')
      Event = {}
      pyloadobj = json.dumps({"Records": [{
        "body": "{\"Message\":\"{\\\"msg\\\": \\\"Test: I am not on PTO today\\\", \\\"chat_id\\\": \\\"19:f33e901e871d4c3c9ebbbbee66e59ebe@thread.skype\\\", \\\"user_id\\\":\\\"blah\\\"}\"}"}]})
      response = client.invoke(FunctionName=lambda_name,InvocationType='Event',Payload = pyloadobj,LogType='None')
      return response

class ptodetectornonptotest(unittest.TestCase):
  """
  Test class
  """
  def test_end_to_end_pto_detector_non_pto_message(self):

    """
    Test method
    """
    ptodetectortest_obj = ptodetectortest()
    logger.info("Step 1: Trigger employee message lambda--------------------------------")
    pto_detector_lambda_name = 'pto_detector'
    response = ptodetectortest_obj.trigger_cron_lambda(pto_detector_lambda_name)
    request_id = response.get('ResponseMetadata')['RequestId']
    logger.info(request_id)
    time.sleep(360)
    client = boto3.client('logs')
    start_query_response = client.start_query(logGroupName=cloudwatch_conf.pto_log_group,\
        startTime=int((datetime.today() - timedelta(minutes=6)).timestamp()),\
            endTime=int(datetime.now().timestamp()),queryString=cloudwatch_conf.query_pto_detector)
    query_id = start_query_response['queryId']
    response = None
    while response == None:
      time.sleep(1)
      response = client.get_query_results(queryId=query_id)
      response_dict = tests.helpers.cloudwatch_helper.get_data_structure(response)
      message = response_dict['results_0_1_value']
    logger.info("-----------------message from cloudwatch logs------------------------------------------")
    logger.info(message)
    logger.info('--------------------asserting message---------------------------------------------------')
    assert message == "Test: I am not on PTO today, blah, 19:f33e901e871d4c3c9ebbbbee66e59ebe@thread.skype\n"
    logger.info("---------------------------------------------------------------------------")
