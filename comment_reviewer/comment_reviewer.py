"""
This Lambda will :
   - Give a list of comment reviewers
"""
import json
import os
import boto3

QUEUE_URL = 'https://sqs.ap-south-1.amazonaws.com/285993504765/skype-sender'
at_Qxf2Bot = '<at id="8:live:.cid.92bd244e945d8335">qxf2bot</at>!'
at_Qxf2Bot_english = '@qxf2bot!'

COMMANDS = [f'comment reviewers, please {at_Qxf2Bot}',
            f'i need comment reviewers {at_Qxf2Bot}',
            f'comment reviewers please {at_Qxf2Bot}',
            f'comment reviewers, please {at_Qxf2Bot_english}',
            f'i need comment reviewers {at_Qxf2Bot_english}',
            f'comment reviewers please {at_Qxf2Bot_english}']

FIRST_SSM = 'first_comment_reviewer_index'
SECOND_SSM= 'second_comment_reviewer_index'
RESET_COMMANDS = [f'reset first comment reviewer {at_Qxf2Bot}',
                f'reset second comment reviewer {at_Qxf2Bot}']


def read_parameter(client, parameter_name, decryption_flag = False):
    "Read a SSM parameter"
    parameter = client.get_parameter(Name=parameter_name, WithDecryption = decryption_flag)

    return parameter['Parameter']['Value']

def write_parameter(client, parameter_name, value, decryption_flag = False):
    "Write to a SSM parameter"
    response = client.put_parameter(
        Name = parameter_name,
        Value = value,
        Overwrite = True
    )

    return True if response['ResponseMetadata']['HTTPStatusCode'] == 200 else False

def get_reviewer_index(reviewer_type):
    "Return the index of the reviewer"
    client = boto3.client("ssm")
    reviewer_index = read_parameter(client, reviewer_type)

    return int(reviewer_index)

def update_reviewer_index(reviewer_type,increment=1):
    "Increment the reviewer index by 1"
    client = boto3.client("ssm")
    reviewer_index = read_parameter(client, reviewer_type)
    write_parameter(client,
    reviewer_type,
    str(int(reviewer_index) + increment))

def get_code_reviewers(reviewer_type):
    "Return a list of primary comment reviewers"
    return os.environ.get(reviewer_type,"").split(',')

def get_message_contents(event):
    "Retrieve the message contents from the SQS event"
    record = event.get('Records')[0]
    message = record.get('body')
    message = json.loads(message)['Message']
    message = json.loads(message)

    return message

def write_message(message, channel):
    "Send a message to Skype Sender"
    sqs = boto3.client('sqs')
    print(channel)
    message = str({'msg':f'{message}', 'channel':channel})
    print(message)
    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=(message))

def in_correct_channel(channel):
    "Is the message in the right channel?"
    return channel == os.environ.get('channel','')

def is_code_reviewer_command(message):
    "Is this a code reviewer command?"
    return message.lower() in COMMANDS

def is_reviewer_reset_command(message):
    "Is this is a reset command?"
    return message.lower() in RESET_COMMANDS

def get_reply():
    "Get the primary and secondary comment reviewers"
    first_comment_reviewers = get_code_reviewers('first_comment_reviewers')
    second_comment_reviewers = get_code_reviewers('second_comment_reviewers')
    first_index = get_reviewer_index(FIRST_SSM)
    second_index = get_reviewer_index(SECOND_SSM)
    first_comment_reviewer = first_comment_reviewers[first_index%len(first_comment_reviewers)]
    second_comment_reviewer = second_comment_reviewers[second_index%len(second_comment_reviewers)]
    reply = f'first comment reviewer: {first_comment_reviewer}\n\nsecond comment reviewer: {second_comment_reviewer}'

    return reply

def update_reviewer_indexes():
    "Increment the reviewer indexes by 1"
    update_reviewer_index(FIRST_SSM)
    update_reviewer_index(SECOND_SSM)

def lambda_handler(event, context):
    "Code reviewer lambda"
    message_contents = get_message_contents(event)
    message = message_contents['msg'].strip()
    channel = message_contents['chat_id']
    user = message_contents['user_id']

    if in_correct_channel(channel):
        if is_code_reviewer_command(message):
            reply = get_reply()
            write_message(reply, os.environ.get('channel',''))
            update_reviewer_indexes()
        if is_reviewer_reset_command(message):
            prev = -1
            curr = -1
            if 'primary' in message.lower():
                prev = get_reviewer_index(FIRST_SSM)
                update_reviewer_index(FIRST_SSM, -1)
                curr = get_reviewer_index(FIRST_SSM)
            if 'secondary' in message.lower():
                prev = get_reviewer_index(SECOND_SSM)
                update_reviewer_index(SECOND_SSM, -1)
                curr = get_reviewer_index(SECOND_SSM)
            message = f'Reset index from {prev} to {curr}'
            write_message(message, os.environ.get('channel',''))

    return {
        'statusCode': 200,
        'body': json.dumps('Done!')
    }