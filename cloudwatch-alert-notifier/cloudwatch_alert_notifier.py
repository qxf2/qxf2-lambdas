"""
This script will send the Cloudwatch Alarm notification messages to skype

"""
import json
import os
import requests


def get_channel_id(channel_name='test'):
    "Set the channel to send the message to"
    channels = json.loads(os.environ.get('SKYPE_CHANNELS').replace("'", "\""))
    channel_id = channels.get(channel_name, 'provide default channel id here')
    return channel_id

def get_alert_message(full_msg):
    "Form alert message to send"
    alarm_message = json.loads(json.loads(full_msg).get("Message", {}))
    alarm_name = alarm_message.get("AlarmName", "Unknown Alarm Name")
    alarm_region = alarm_message.get("Region", "Unknown Region")
    alarm_state_reason = alarm_message.get("NewStateReason", "Unknown State Reason")
    alarm_state_change_time = alarm_message.get("StateChangeTime", "Unknown State Change Time")
    alarm_description = alarm_message.get("AlarmDescription", "Unknown Alarm Description")

    # Form meaningful alert message
    alert_message = (
        f"<b>ALERT:</b> {alarm_name} in {alarm_region}\n"
        f"<b>Description:</b> {alarm_description}\n"
        f"<b>State Change Time:</b> {alarm_state_change_time}\n"
        f"<b>Reason:</b> {alarm_state_reason}\n"
    )
    return alert_message

def post_message(event, context=None):
    "Post a message"
    print(f'The trigger event is: {event}')
    for record in event['Records']:
        full_msg = record['body']
        alert_message = get_alert_message(full_msg)
        # Print the alert message
        print(alert_message)
        channel_id = get_channel_id()
        url = os.environ['SKYPE_SENDER_ENDPOINT']
        data = {
            'API_KEY': os.environ['API_TOKEN'],
            'msg': alert_message,
            'channel': channel_id
        }
        response = requests.post(url, json=data, timeout=10)
        print(f'Received {response.json()} for {alert_message}')
