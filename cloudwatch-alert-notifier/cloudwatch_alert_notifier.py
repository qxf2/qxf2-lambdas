"""
This script will send the Cloudwatch Alarm notification messages to skype

"""
import json
import os
import requests

def get_dict(my_string):
    "Return a dict from a string"
    my_string = my_string.replace("'", "\"")
    my_string = json.loads(my_string)
    return my_string

def get_channel_id():
    "Set the channel to send the message to"
    channel = 'test'
    channels = get_dict(os.environ.get('SKYPE_CHANNELS'))
    channel_id = channels.get(channel,channel)
    return channel_id

def get_alert_message(full_msg):
    "Form alert message to send"
    alarm_message = json.loads(json.loads(full_msg)["Message"])
    alarm_name = alarm_message["AlarmName"]
    alarm_region = alarm_message["Region"]
    alarm_state_reason = alarm_message["NewStateReason"]
    alarm_state_change_time = alarm_message["StateChangeTime"]
    alarm_arn = alarm_message["AlarmArn"]
    alarm_description = alarm_message["AlarmDescription"]
    
    # Form meaningful alert message
    alert_message = f"<b>ALERT:</b> {alarm_name} in {alarm_region}\n<b>Description:</b> {alarm_description}\n<b>State Change Time:</b> {alarm_state_change_time}\n<b>Reason:</b> {alarm_state_reason}\n<b>Alarm ARN:</b> {alarm_arn}"
    return alert_message
    

def post_message(event, context=None):
    "Post a message"
    print(f'The trigger event is: {event}')
    full_msg = event['Records'][0]['body']
    alert_message = get_alert_message(full_msg)
    # Print the alert message
    print(alert_message)
    channel_id = get_channel_id()
    url = os.environ['SKYPE_SENDER_ENDPOINT']
    data = {'API_KEY' : os.environ['API_TOKEN'],
        'msg' : alert_message,
        'channel' : channel_id}
    response = requests.post(url, json=data)
    print(f'Received {response.json()} for {alert_message}')