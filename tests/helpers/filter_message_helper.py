"""
Helper module for filter message functionality
"""
import os
import sys
import json
import pytest
import requests
import tests.conf.channel_configuration_conf as channel_conf
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#Defining current file path
CURR_FILE_PATH = os.path.dirname(os.path.abspath(__file__))
MESSAGES_PATH = os.path.join(CURR_FILE_PATH, '')
DAILY_MESSAGES_URL = 'https://daily-messages.qxf2.com'

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

def get_dict(body_string):
    """
    Generates dict from message body
    :param string
    :return dict object
    """
    body_string = json.dumps(body_string)
    body_string = body_string.replace("'", "\"")
    body_string = json.loads(body_string)
    message_body_obj = json.loads(body_string)

    return message_body_obj

def get_message_body(message):
    """
    This method will return message body
    """
    msg_body = ""
    if 'Messages' in message:
        for message in message['Messages']:
            if 'Body' in message.keys():
                message_body_obj = get_dict(message['Body'])
                if 'Message' in message_body_obj.keys():
                    msg_body = get_dict(message_body_obj['Message'])
                else:
                    print("Message key is not present in the Message Body")
                    sys.exit()
            else:
                print("Message does not contain Body")
                sys.exit()

    else:
        print("No messages are retrieved")
        with pytest.raises(SystemExit):
            sys.exit()

    return msg_body

def filter_message(message,chat_id,user_id):
    """
    Filter method based on chat_id and user_id
    return: Boolean value
    """
    message_body = get_message_body(message)
    if message_body is not None:
        if "chat_id" in message_body and "user_id" in message_body:
            if message_body['chat_id']==chat_id and message_body['user_id']==user_id:
                print(f'message is from test channel and  sender is skype sender lambda')
            else:
                print(f'Neither message is from test channel nor sender is skype sender lambda')
        else:
            print(f'Message does not contain required keys')
    else:
        print(f'Message body is not none')

    return True

def compare_message_cloudwatch_log(message_on_channel, message_cloudwatch):
    """
    compare message with cloudwatch log message
    """
    result_flag = False
    if message_on_channel == message_cloudwatch:
        result_flag = True
    else:
        result_flag = False

    return result_flag

def get_message(message):
    """
    Fetches message from sqs queue
    """
    message_body = get_message_body(message)

    if message_body is not None:
        if "msg" in message_body:
            return message_body['msg']
        else:
            print(f'Message body does not contain message key')
    else:
        print(f'Message body is none')

def compare_message_with_file(message, endpoint, base_url=DAILY_MESSAGES_URL):
    """
    Compare message with the file on daily-messages app
    """
    result_flag = False
    response = requests.get(base_url+endpoint)
    all_messages = response.json().get('msg',[])
    if message in all_messages:
        result_flag = True

    return result_flag

def validate_message_with_culture_file(message_on_channel):
    """
    Asserting message on channel with culture file
    """
    result_flag = False
    if message_on_channel is not None:
        endpoint = '/culture/all'
        result_flag = compare_message_with_file(message_on_channel, endpoint)
        if result_flag is True:
            print(Style.CYAN + '---------------------------\
                ------------------------------------------------')
            print(Style.CYAN + 'Step 3b. Validating \
                message with culture file------------------------------')
            print(Style.GREEN + 'Message \
                on channel does match with culture file')
            print(Style.CYAN + '-----------\
                ----------------------------------------------------------------')
        else:
            print(Style.CYAN + '------------\
                ---------------------------------------------------------------')
            print(Style.GREEN + 'Message \
                on channel does match with culture file')
            print(Style.CYAN + '---------\
                ------------------------------------------------------------------')
    else:
        print(Style.CYAN + 'There is no message on channel')

    return result_flag

def validate_message_with_cloudwatch_logs(message_on_channel,message_cloudwatch):
    """
    Asserting method on channels with cloudwatch logs
    """
    result_flag = False
    if message_on_channel is not None:
        result_flag = compare_message_cloudwatch_log(message_on_channel,message_cloudwatch)
        if result_flag is True:
            print(Style.CYAN + '---------------\
                ------------------------------------------------------------')
            print(Style.CYAN + 'Step 3a. Validating \
                message with Skype listner SQS Queue-------------------')
            print(Style.GREEN + 'Message on channel \
                does match with the message from cloudwatch logs')
            print(Style.CYAN + '----------------------\
                -----------------------------------------------------')
            result_flag = validate_message_with_culture_file(message_on_channel)
        else:
            print(Style.CYAN + '-------------\
                --------------------------------------------------------------')
            print(Style.RED + 'Message on channel does not match with \
                the message from cloudwatch logs')
            print(Style.CYAN + '---------------------\
                ------------------------------------------------------')
    else:
            print(Style.CYAN + '---------------------------\
                ------------------------------------------------')
            print("No message on channel")
            print(Style.CYAN + '------------------------------\
                ---------------------------------------------')

    return result_flag

def publish_compare_result(message,message_cloudwatch):
    """
    Publish compare result
    """
    result_flag = filter_message\
        (message,channel_conf.chat_id,channel_conf.user_id)
    if result_flag is True:
        message_on_channel= get_message(message)
        result_flag = validate_message_with_cloudwatch_logs(message_on_channel,message_cloudwatch)
    else:
        print(Style.CYAN + '---------------------------------\
            ------------------------------------------')
        print(Style.CYAN + 'No message polled from the queue at this time')
        print(Style.CYAN + '----------------------------\
            -----------------------------------------------')
    return result_flag
