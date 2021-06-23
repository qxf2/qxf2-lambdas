import json
import boto3
import os
import requests

BASE_URL = os.environ.get('BASE_URL')
PASSWORD = os.environ.get('PASSWORD')
USERNAME = os.environ.get('USERNAME')

def authenticate():
    "Return an authenticate code"
    query = f"""mutation {{
        auth(password: "{PASSWORD}", username: "{USERNAME}") {{
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
                    lastname
                    dateJoined
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


def lambda_handler(event, context):
    all_employees = get_all_employees()
    return {
        'statusCode': 200,
        'body': all_employees
    }
