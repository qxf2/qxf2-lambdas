"""
Lambda to to pull URL from ETC channel messages
"""
import json
import os
import boto3
import requests
import re

def clean_message(message):
    "Clean up the message received"
    message = message.replace("'", '-')
    message = message.replace('"', '-')

    return message

def get_message_contents(event):
    "Retrieve the message contents from the SQS event"
    record = event.get('Records')[0]
    message = record.get('body')
    message = json.loads(message)['Message']
    message = json.loads(message)
    
    return message

def get_url(message):
    "Get the URL from the message"
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,message)      
    return [x[0] for x in url]

def generate_bearer_key():
    """
    Assuming there is need to generate a Key may ve bearer key 
    using client id and secretkey
    using client and secret key generate the bearer key and use it
    """

    #url to create token for google auth - if its not same always then call this method to generate this
    url = "http://.../authenticate"
    payload = json.dumps({
            "client_id": "",
            "client_secret": ""
            })
    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    new_reponse = response.text

    return new_reponse


def post_to_newsletter(final_url):
    "Method to call the newsletter API and post the url"
    
    #generate authkey everytime for the request if not static value
    APP_AUTH = 'Bearer {}'.format(generate_bearer_key())

    headers = {
        'Content-Type': 'application/json',
        'Authorization': APP_AUTH
        }

    #newsletter app url currently using my own newsletter ec2 setup
    app_url= "http://...:5000/articles"
    payload=payload={'url': final_url,
        'category_id': '2',
        'description': 'Adding Description through API',
        'title': 'Adding title through API',
        'time': '5'}
    payloadJson = json.dumps(payload)
    response = response = requests.request("POST", app_url, headers=headers, data=payload)
    print(response.status_code)
    return response.status_code

def lambda_handler(event, context):
    """
    Method run when Lambda is triggered
    calls the filtering logic
    calls the logic to post to endpoint
    """
    content = get_message_contents(event)
    message = content['msg']
    channel = content['chat_id']
    user = content['user_id']
    print(f'{message}, {user}, {channel}')
    
    response=""
    final_url=""
    if channel == os.environ.get('ETC_CHANNEL') and user != os.environ.get('Qxf2Bot_USER'):
        print("Getting message posted on ETC ")
        cleaned_message = clean_message(message)
        final_url=get_url(cleaned_message)
        #Filtered URL is printed by lambda
        print("Final url is :",final_url)
        if final_url:
            #till we get correct endpoint details next line will throw error
            #it worked with my ec2 instance of newsletter which didnt have auth code
            response = post_to_newsletter(final_url)
        else:
            print("message does not contain any url")
    else:
        print("Message not from ETC channel")

    return {
        'statusCode': response,
        'body': json.dumps(final_url)
    }
    
