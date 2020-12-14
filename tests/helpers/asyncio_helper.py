"""
Helper module for asyncio methods
"""
import asyncio
import logging
import helpers.filter_message_helper
import helpers.sqs_helper
import conf.sqs_utilities_conf as queue_url_conf

async def validate_message_with_sqs(queue_url, message_cloudwatch):
    """
    Validates message from sqs queue with cloudwatch logs
    :param queue_url: URL of the SQS queue
    :message_cloudwatch: Message received from cloudwatch logs
    """
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    message = helpers.sqs_helper.get_message_from_queue(queue_url)
    result_flag = helpers.filter_message_helper.publish_compare_result(message,message_cloudwatch)

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
