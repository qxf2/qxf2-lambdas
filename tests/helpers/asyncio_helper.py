"""
Helper module for asyncio methods
"""
import sys
import asyncio
import logging
import tests.helpers.filter_message_helper
import tests.helpers.sqs_helper
import tests.conf.sqs_utilities_conf as queue_url_conf

# Declaring class Style
class Style():
    """
    Declaring Style class
    """
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

async def validate_message_with_sqs(queue_url, message_cloudwatch):
    """
    Validates message from sqs queue with cloudwatch logs
    :param queue_url: URL of the SQS queue
    :message_cloudwatch: Message received from cloudwatch logs
    """
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    message = tests.helpers.sqs_helper.get_message_from_queue(queue_url)
    result_flag = tests.helpers.filter_message_helper.publish_compare_result\
        (message,message_cloudwatch)
    if result_flag is True:
        sys.exit()

    return result_flag

async def poll_message(message_cloudwatch):
    """
    Schedule calls concurrently
    """
    while True:
        tasks = []
        for every_queue_url in queue_url_conf.QUEUE_URL_LIST:
            tasks.append(validate_message_with_sqs(every_queue_url,message_cloudwatch))
        result = await asyncio.gather(*tasks)
