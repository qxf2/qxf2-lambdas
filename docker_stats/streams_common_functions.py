"""
Module to contain functions that are common across various streams:
- stats fetching scripts.
- score generation scripts.
"""
import os
import sys
import boto3
import requests
import conf as cf
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



def get_current_docker_data(docker_url):
    "Gets the current data from Docker Hub for all containers."
    response = requests.get(docker_url)
    result = response.json()
    return result

def write_into_db(info, table_name):
    "Writes info into DynamoDB table."
    dynamodb = None
    # Initialise a DynomoDB table resource.
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
    if table_name in cf.DOCKER_STATS_TABLE_NAME:
        try:
            with table.batch_writer() as batch:
                for container_stats in info:
                    date = container_stats['date']
                    container_name = container_stats['image_name']
                    print("Adding record for {} on {} to DynamoDB table {}."\
                            .format(container_name, date, table_name))
                    batch.put_item(Item=container_stats)
        except Exception:
            raise Exception('Exception while inserting data into table.')
