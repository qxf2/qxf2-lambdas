"""
This Lambda will take a user message and pass it to ChatGPT.
It will then send back ChatGPT's reply to the user.
"""
import json
import os
import boto3
import openai

QUEUE_URL = os.getenv(SKYPE_SENDER_QUEUE, "INVALID SKYPE SENDER QUEUE")
at_Qxf2Bot = os.getenv(AT_QXF2BOT, "INVALID QXF2BOT SETTING")
at_Qxf2Bot_english = "@qxf2bot!"
COMMANDS = [
    f"help {at_Qxf2Bot}",
    f"help us {at_Qxf2Bot}",
    f"help me {at_Qxf2Bot}",
    f"help {at_Qxf2Bot_english}",
    f"help me {at_Qxf2Bot_english}",
    f"help us {at_Qxf2Bot_english}",
]


def get_message_contents(event):
    "Retrieve the message contents from the SQS event"
    messages = []
    for record in event.get("Records"):
        message = record.get("body")
        message = json.loads(message)["Message"]
        message = json.loads(message)
        messages.append(message)

    return messages


def write_message(message, channel):
    "Send a message to Skype Sender"
    sqs = boto3.client("sqs")
    print(channel)
    message = str({"msg": f"{message}", "channel": channel})
    print(message)
    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=(message))


def is_help_command(message):
    "Is this a user wanting to talk to ChatGPT?"
    result_flag = False
    for command in COMMANDS:
        if command in message.lower():
            result_flag = True
            break

    return result_flag


def get_reply(message):
    "Get the reply from ChatGPT"
    openai.api_key = os.getenv("OPENAI_API_KEY", "")
    model_engine = os.getenv("MODEL_ENGINE", "")
    response = openai.ChatCompletion.create(
        model=model_engine, messages=[{"role": "user", "content": message}]
    )
    reply = f"{response['choices'][0]['message']['content']}. Usage stats: {response['usage']['total_tokens']}"

    return reply


def lambda_handler(event, context):
    "Code reviewer lambda"
    message_contents = get_message_contents(event)
    for message_content in message_contents:
        message = message_content["msg"].strip()
        channel = message_content["chat_id"]
        user = message_content["user_id"]
        if is_help_command(message):
            reply = get_reply(message)
            write_message(reply, channel)
        
    return {"statusCode": 200, "body": json.dumps("Done!")}
