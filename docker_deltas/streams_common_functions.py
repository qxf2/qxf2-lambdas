"""
Module to contain functions that are common across various streams:
- stats fetching scripts.
- score generation scripts.
"""
import sys
import os
import boto3
import requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import conf as conf


def get_substreams(stream):
    "Returns all the sub-streams for the provided stream."
    substreams = get_current_docker_data()
    return substreams

def get_current_docker_data():
    "Gets the current data from Docker Hub for all containers."
    response = requests.get(conf.DOCKER_HUB_URL)
    result = response.json()
    return result

def read_db(stream_access_info, table_name, date):
    "Retrieves items that match the criterias, from the DynamoDB table."
    dynamodb = None
    stats_obj = [] #list of dicts
    # Collect all sub-streams.
    substreams_info = get_substreams(table_name)
    # Initialise a DynomoDB table resource.
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
    if table_name in (conf.DOCKER_STATS_TABLE_NAME):
        try:
            for container_data in substreams_info['results']:
                response = table.get_item(\
                    Key={'date':date,\
                         'image_name':container_data['name']}\
                )
                stats_obj.append(response['Item'])
        except Exception:
            raise Exception('Exception while reading data from table.')
    return stats_obj

def write_into_db(info, table_name):
    "Writes info into DynamoDB table."
    dynamodb = None
    # Initialise a DynomoDB table resource.
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
    if table_name in (conf.DOCKER_DELTAS_TABLE_NAME):
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
