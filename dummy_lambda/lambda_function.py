"""
Simplest lambda to play with GitHub actions
Try 1: Failed. Simply change requirements.txt path
Try 2: Changing the action to include a directory
"""
import json

def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
