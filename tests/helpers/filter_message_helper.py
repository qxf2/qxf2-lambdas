"""
Helper module for filter message functionality
"""
import os
import sys
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
        sys.exit()

    return msg_body

def filter_message(message,chat_id,user_id):
    """
    Filter method based on chat_id and user_id
    return: Boolean value
    """
    message_body = get_message_body(message)
    if message_body['chat_id']==chat_id and message_body['user_id']==user_id:
        return True
    else:
        print(f'Neither message is from test channel neither sender is skype sender lambda')

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

    return message_body['msg']

def compare_message_with_file(message, file_name):
    """
    Compare message with file
    """
    result_flag = False
    with open(file_name, 'r') as file_handler:
        lines = [line.strip() for line in file_handler]
        if message in lines:
            result_flag = True
        else:
            result_flag = False

    return result_flag
