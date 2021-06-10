"""
This Lambda will :
   - Get a list of active Qxf2 employees skype id every thursday and remind them to fill the survey via skype sender
   - Get a list of Qxf2 employees who have not filled the survey every friday and remind them one more time to fill the survey via skype sender
"""
import os
import boto3
import json
import requests
from datetime import date

BASE_URL = 'https://qxf2-employees.qxf2.com/graphql'
QUEUE_URL = 'https://sqs.ap-south-1.amazonaws.com/285993504765/skype-sender'
NOT_RESPONDED_USERS_URL = ''

def authenticate():
    "Return an authenticate code"
    query = f"""mutation {{
        auth(password: "{os.environ.get('PASSWORD')}", username:"{os.environ.get('USERNAME')}" ) {{
            accessToken
            refreshToken
            }}
        }}
    """
    response = requests.post(url = BASE_URL, json = {'query': query})
    return response.json().get('data',{}).get('auth',{}).get('accessToken',None)

def get_all_employees():
    "Query allEmployees"
    query = """query
    findAllEmployees{
        allEmployees{
            edges{
                node{
                    email
                    firstname
                    skypeId
                    isActive
                }
            }
        }
    }"""
    access_token = authenticate()
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url = BASE_URL, json = {'query': query}, headers =\
        headers)
    all_employees = response.json().get('data', {}).get('allEmployees', {}).get('edges', [])
    return all_employees

def write_message(survey_reminder_message, channel):
    "Send a message to Skype Sender"
    sqs = boto3.client('sqs')
    message = str({'msg':f'{survey_reminder}', 'channel':channel})
    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=(message))

def survey_reminder():
    emp_data = get_all_employees()
    if date.today().weekday() == 3:
        for each_node in emp_data:
            msg = f"Hey {each_node['node']['firstname']} ,it's time to take the help survey!!"
            write_message(msg,each_node['node']['skypeId'])
    elif date.today().weekday() == 4:
        non_responded_users = requests.get(NOT_RESPONDED_USERS_URL,headers={'Accept':'application/json','User':os.environ.get('AUTHORISED_USER')})
        msg = 'Non responded message'
    return msg

def lambda_handler(event, context):
    "lambda entry point"
    message = survey_reminder()

    