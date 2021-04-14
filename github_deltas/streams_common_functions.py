"""
    Module to contain the DynamoDB operations related to QElo.
"""
import re
import boto3
import conf as sf
from github import Github
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

def extract_substream_names(substreams_data, key):
    "Extracts the name of substreams from the complete substreams data."
    substreams = [substream_data[key] for substream_data in substreams_data]
    return substreams

def read_substreams(table_name, date):
    "Retrieves substreams from the corresponding DynamoDB table."
    dynamodb = boto3.resource('dynamodb') # Initialise a DynomoDB table resource.
    table = dynamodb.Table(table_name)
    try:
        filtering_exp = Key('date').eq(date)
        response = table.query(KeyConditionExpression=filtering_exp)
        if re.search(r'^github', table_name):
            data = extract_substream_names(response['Items'], 'repo_name')
        else:
            data = extract_substream_names(response['Items'], 'image_name')
        print(f"\n Read records for {date} successfully from DynamoDB table {table_name}.")
        return data
    except Exception:
        raise Exception('Exception while reading data from table.')

def read_github_table(table_name, date, substreams):
    "Retrieves items that match the criterias, from corresponding GitHub DynamoDB table."
    data = [] #list of dicts
    dynamodb = boto3.resource('dynamodb') # Initialise a DynomoDB table resource.
    table = dynamodb.Table(table_name)
    try:
        for substream in substreams:
            response = table.get_item(
                Key={\
                        'date':date,\
                        'repo_name':substream\
                    }\
                )
            data.append(response['Item'])
        print(f"\n Read records for {date} successfully from DynamoDB table {table_name}.")
        return data
    except Exception:
        raise Exception('Exception while reading data from table.')

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
