"""
Helper module for asyncio methods
"""
import os
import sys
import asyncio
import logging
import helpers.filter_message_helper
import helpers.sqs_helper
import conf.channel_configuration_conf as channel_conf
import conf.sqs_utilities_conf as queue_url_conf
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#Defining current file path
CURR_FILE_PATH = os.path.dirname(os.path.abspath(__file__))
MESSAGES_PATH = os.path.join(CURR_FILE_PATH, '')
CULTURE_FILE = os.path.join(MESSAGES_PATH, 'culture.txt')

#setting environment variable
os.environ['chat_id']= channel_conf.chat_id
os.environ['user_id'] = channel_conf.user_id

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
    message = helpers.sqs_helper.get_message_from_queue(queue_url)
    result_flag = helpers.filter_message_helper.filter_message\
        (message,channel_conf.chat_id,channel_conf.user_id)
    if result_flag is True:
        message_on_channel= helpers.filter_message_helper.get_message(message)
        if message_on_channel is not None:
            assert helpers.filter_message_helper.compare_message_cloudwatch_log\
                (message_on_channel,message_cloudwatch)
            if result_flag is True:
                print(Style.CYAN + f'---------------\
                    ------------------------------------------------------------')
                print(Style.CYAN + f'Step 3a. Validating \
                    message with Skype listner SQS Queue-------------------')
                print(Style.GREEN + f'Message {message_on_channel} \
                    does match with {message_cloudwatch} the message from cloudwatch logs')
                print(Style.CYAN + f'----------------------\
                    -----------------------------------------------------')
                assert helpers.filter_message_helper.compare_message_with_file\
                    (message_on_channel,CULTURE_FILE)
                if result_flag is True:
                    print(Style.CYAN + f'---------------------------\
                        ------------------------------------------------')
                    print(Style.CYAN + f'Step 3b. Validating \
                        message with culture file------------------------------')
                    print(Style.GREEN + f'Message \
                        {message_on_channel} does match with culture file')
                    print(Style.CYAN + f'-----------\
                        ----------------------------------------------------------------')
                else:
                    print(Style.CYAN + f'------------\
                        ---------------------------------------------------------------')
                    print(Style.GREEN + f'Message \
                        {message_on_channel} does match with culture file')
                    print(Style.CYAN + f'---------\
                        ------------------------------------------------------------------')
                sys.exit()
            else:
                print(Style.CYAN + f'-------------\
                    --------------------------------------------------------------')
                print(Style.RED + f'Message {message_on_channel} does not match with \
                    {message_cloudwatch} the message from cloudwatch logs')
                print(Style.CYAN + f'---------------------\
                    ------------------------------------------------------')
        else:
            print(Style.CYAN + f'---------------------------\
                ------------------------------------------------')
            print("No message on channel")
            print(Style.CYAN + f'------------------------------\
                ---------------------------------------------')
    else:
        print(Style.CYAN + f'---------------------------------\
            ------------------------------------------')
        print(Style.CYAN + f'No message polled from the queue {queue_url} at this time')
        print(Style.CYAN + f'----------------------------\
            -----------------------------------------------')

    return True

async def poll_message(message_cloudwatch):
    """
    Schedule calls concurrently
    """
    while True:
        tasks = []
        for every_queue_url in queue_url_conf.QUEUE_URL_LIST:
            tasks.append(validate_message_with_sqs(every_queue_url,message_cloudwatch))
        result = await asyncio.gather(*tasks)
