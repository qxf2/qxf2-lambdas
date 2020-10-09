"""
This Python module contains function that
performs various dynamodb operations.
"""
import os
import sys
import boto3
import requests
import conf as cf
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_current_docker_data(docker_url):
    "Gets the current data from Docker Hub URL for all containers."
    response = requests.get(docker_url)
    result = response.json()
    return result['results']

def write_into_table(items, table_name):
    "Writes items/records into DynamoDB table."
    dynamodb = None
    # Initialise a DynomoDB table resource.
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
    try:
        with table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)
        print(f"Added today's records successfully into DynamoDB table {table_name}.")
        return 'data collected in {} table'.format(table_name)
    except Exception:
        return 'Exception while inserting data into {} table'.format(table_name)
