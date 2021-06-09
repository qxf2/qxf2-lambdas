"""
Simplest lambda to play with GitHub actions
"""
import json
import requests

def action_handler(event, context):
    print("This is lamda entry point")
    response = requests.get('https://api.github.com')
    print("The respone is ", response)
    if response.status_code == 200:
        print('Success for code review!')
    elif response.status_code == 404:
        print('Not Found for code review!.')


if __name__ == "__main__":
    print("Hi, I am testing no function scenario")
    lambda_handler("", "")