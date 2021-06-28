"""
This End to end test employee skype message covers following:
Step 1: Trigger non pto detector message from pto detector lambda
Step 2: Assert message from cloudwatch log with message sent
Step 3: Assert logstream from the record containing message and false flag
"""

import os
import sys
import time
import ast
import asyncio
from datetime import datetime, timedelta
import json
import logging
import boto3
import pytest
import unittest
import tests.helpers.cloudwatch_helper
import tests.helpers.generic_utils_helper as generic_utils
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
  logger = logging.getLogger(__name__)

  def __init__(self):
      """
      Initilalise class
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

  def get_query_id(self):
    """
    Method returns query id
    """
    query_id = None
    while query_id == None:
      client = boto3.client('logs')
      start_query_response = client.start_query(logGroupName=cloudwatch_conf.pto_log_group,\
        startTime=int((datetime.today() - timedelta(minutes=6)).timestamp()),\
            endTime=int(datetime.now().timestamp()),queryString=cloudwatch_conf.query_pto_detector)
      query_id = start_query_response['queryId']

    return query_id

  def get_message_from_pto_detector_logs(self,query_id):
    """
    Method to get message from pto_detector lambda insights
    """
    response = None
    message = None
    while response == None:
      generic_utils.wait(1)
      client = boto3.client('logs')
      response = client.get_query_results(queryId=query_id)
      response_dict = tests.helpers.cloudwatch_helper.get_data_structure(response)
      if "results_0_1_value" in response_dict.keys():
        message = response_dict['results_0_1_value']

    return message

  def get_logstream_from_ptr_value(self,query_id):
    """
    Method to fetch logstream ptr value
    """
    ptr_value = None
    response = None
    logstream = None
    while response == None:
      generic_utils.wait(1)
      client = boto3.client('logs')
      response = client.get_query_results(queryId=query_id)
      response_dict = tests.helpers.cloudwatch_helper.get_data_structure(response)
      logger.info(response_dict)
      ptr_value = response_dict['results_0_2_value']
      if ptr_value:
        response = client.get_log_record(logRecordPointer=ptr_value)
        response_dict = tests.helpers.cloudwatch_helper.get_data_structure(response)
        logstream = response_dict['logRecord_@logStream']

    return logstream

  def get_query_id_from_flag_message(self):
    """
    Method to get query id from flag message
    """
    client = boto3.client('logs')
    start_query_response = client.start_query(logGroupName=cloudwatch_conf.pto_log_group,\
        startTime=int((datetime.today() - timedelta(minutes=7)).timestamp()),\
            endTime=int(datetime.now().timestamp()),queryString=cloudwatch_conf.query_pto_detector_flag)
    query_id = start_query_response['queryId']

    return query_id

  def get_logstream_from_flag_value(self,query_id):
    """
    Method to fetch logstream from flag value
    """
    response = None
    logstream = None
    while response == None:
      generic_utils.wait(1)
      client = boto3.client('logs')
      response = client.get_query_results(queryId=query_id)
      response_dict = tests.helpers.cloudwatch_helper.get_data_structure(response)
      logstream = response_dict['results_0_2_value']

    return logstream

class ptodetectornonptotest(unittest.TestCase):
  """
  Test class
  """
  def test_end_to_end_pto_detector_non_pto_message(self):

    """
    Test method
    """
    logger.info("---------------------------------------------------------------------------")
    ptodetectortest_obj = ptodetectortest()
    logger.info("Step 1: Trigger pto detector lambda--------------------------------")
    pto_detector_lambda_name = 'pto_detector'
    ptodetectortest_obj.trigger_cron_lambda(pto_detector_lambda_name)
    logger.info("-------------waiting till we get query id--------------------------------------------------")
    generic_utils.wait(360)
    logger.info('-------------printing query id fetched using query containing message----------------------')
    query_id = ptodetectortest_obj.get_query_id()
    logger.info(query_id)
    logger.info('-----------------fetching original message from cloudwatch logs------------------------------------------')
    message_from_logs = ptodetectortest_obj.get_message_from_pto_detector_logs(query_id)
    logger.info("Step 2: Assert message from cloudwatch log with message sent--------------------------------")
    assert message_from_logs == "Test: I am not on PTO today, blah, 19:f33e901e871d4c3c9ebbbbee66e59ebe@thread.skype\n"
    logger.info('---------------------Getting log stream from log reord pointer of original message-------------------------------')
    logstream = ptodetectortest_obj.get_logstream_from_ptr_value(query_id)
    logger.info(logstream)
    logger.info('--------------Printing query_id from flag message-------------------------------------------------')
    query_id_from_flag = ptodetectortest_obj.get_query_id_from_flag_message()
    logger.info(query_id_from_flag)
    logger.info('---------------------Getting log stream for flag message-------------------------------')
    logstream_from_flag = ptodetectortest_obj.get_logstream_from_flag_value(query_id_from_flag)
    logger.info(logstream_from_flag)
    logger.info("Step 3: Assert logstream from the record containing message and false flag----------------------------------------------------")
    assert logstream == logstream_from_flag
    logger.info("---------------------------------------------------------------------------")
