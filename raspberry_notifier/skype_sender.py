"""
This script will let a user send messages on some Qxf2 Skype channels
"""
import json
import requests
import config


def send_skype_message(message):
    "Posts a message on set Skype channel"
    try:
        headers = {
            "Content-Type": "application/json",
        }
        data = {}
        data["msg"] = message
        data["channel"] = config.SKYPE_CHANNEL
        data["API_KEY"] = config.API_KEY

        response = requests.post(config.SKYPE_URL, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            print(f'Successfully sent the Skype message - {message}')
        else:
            print(f'Failed to send Skype message', level='error')
    except Exception as err:
        raise Exception(f'Unable to post message to Skype channel, due to {err}')
