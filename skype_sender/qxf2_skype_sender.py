"""
This script will let a user send messages on some Qxf2 Skype channels
Some of the commonly used channels are listed in the environment variable SKYPE_CHANNELS

"""
import json
import os
import requests

def get_dict(my_string):
    "Return a dict from a string"
    my_string = my_string.replace("'", "\"")
    my_string = json.loads(my_string)

    return my_string

def get_channel_id(msg_body):
    "Return the channel id, default to main if channel not available"
    channel = msg_body.get('channel','main')
    if channel[-6:].lower() == '.skype':
        channel = channel.lower()
    channels = get_dict(os.environ.get('SKYPE_CHANNELS'))
    channel_id = channels.get(channel,channel)

    return channel_id

def post_message(event, context=None):
    "Post a message"
    print(f'The trigger event is: {event}')
    full_msg = get_dict(event['Records'][0]['body'])
    if 'msg' in full_msg.keys():
        msg = full_msg['msg']
        channel_id = get_channel_id(full_msg)
        url = os.environ['SKYPE_SENDER_ENDPOINT']
        data = {'API_KEY' : os.environ['API_TOKEN'],
            'msg' : msg,
            'channel' : channel_id}
        response = requests.post(url, json=data)
        print(f'Received {response.json()} for {msg}')
    else:
        print('The event had no key called msg in it\'s body')
