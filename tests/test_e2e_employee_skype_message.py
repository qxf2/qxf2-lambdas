"""
This End to end test employee skype message covers following:
Setup- Purging SQS queue
Step 1: Triggeering employee message lambda
Step 2: Printing message from cloudwatch logs
Step 3: verifying message with skype-listner sqs queue and culture file
"""

import os
import sys
import time
import asyncio
import logging
import helpers.cloudwatch_helper
import helpers.lambda_helper
import helpers.sqs_helper
import helpers.asyncio_helper
from pythonjsonlogger import jsonlogger
import conf.cloudwatch_configuration_conf as cloudwatch_conf
import conf.sqs_utilities_conf as queue_url_conf
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# logging
log_handler = logging.StreamHandler()
log_handler.setFormatter(jsonlogger.JsonFormatter())
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

# Declaring class for test object
class Skypemessagetest():
    """
    Class for test object
    """
    logger = logging.getLogger(__name__)
    def __init__(self):
        """
        Initilalise class
        """
    def get_request_id(self):
        """
        get the response from lambda
        """
        request_id = helpers.lambda_helper.get_request_id_from_lambda_response()

        return request_id

    def get_message_from_cloudwatch_log_ptr(self):
        """
        Method to get message from cloudwatch log pointer
        """
        message = None
        for i in range(1, 6):
            ptr_value = helpers.cloudwatch_helper.get_ptr_value\
                (cloudwatch_conf.log_group_bot_sender,cloudwatch_conf.query_skype_sender)
            if ptr_value:
                message = helpers.cloudwatch_helper.get_message(ptr_value)
                break
            time.sleep(1)

        return message

    def clear_queues(self):
        """
        Method to clear queues
        """
        for every_queue_url in queue_url_conf.QUEUE_URL_LIST:
            helpers.sqs_helper.purge_sqs_queue(every_queue_url)
            time.sleep(1)

if __name__ == '__main__':
    Skypemessagetest_obj = Skypemessagetest()
    logger.info("Setup- Purging SQS queue")
    logger.info("---------------------------------------------------------------------------")
    Skypemessagetest_obj.clear_queues()
    logger.info("Step 1: Triggeering employee message lambda--------------------------------")
    request_id = Skypemessagetest_obj.get_request_id()
    logger.info("---------------------------------------------------------------------------")
    logger.info("Step 2: Printing message from cloudwatch logs------------------------------")
    time.sleep(240)
    message = Skypemessagetest_obj.get_message_from_cloudwatch_log_ptr()
    logger.info("---------------------------------------------------------------------------")
    logger.info(message)
    logger.info("-------------------------------------------------------------------------- ")
    logger.info("Step 3: verifying message with skype-listner sqs queue and culture file----")
    asyncio.run(helpers.asyncio_helper.poll_message(message))
    logger.info("-------------------------------------------------------------------------- ")
