"""
Module to contain the DynamoDB functions.
"""
import re
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

def init_table(table_name):
    "Initializes and returns the DynamoDB table resource"
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    return table

def extract_substream_names(substreams_data, key):
    "Extracts the name of substreams from the complete substreams data."
    substreams = [substream_data[key] for substream_data in substreams_data]
    return substreams

def read_substreams(table_name, date):
    "Retrieves substreams from the corresponding DynamoDB table."
    try:
        table = init_table(table_name)
        filtering_exp = Key('date').eq(date)
        response = table.query(KeyConditionExpression=filtering_exp)
        if re.search(r'^github', table_name):
            data = extract_substream_names(response['Items'], 'repo_name')
        else:
            data = extract_substream_names(response['Items'], 'image_name')
        print(f"\n Read records for {date} successfully from DynamoDB table {table_name}.")
        return data
    except ClientError as dynamodb_error:
        print(f'\n Error while reading from table {table_name} : \n {dynamodb_error.response}')
        raise Exception('Exception encountered and run aborted!.')
    except Exception:
        raise Exception('Exception while reading data from table.')

def read_github_table(table_name, date, substreams):
    "Retrieves items that match the criterias, from corresponding GitHub DynamoDB table."
    data = [] #list of dicts
    try:
        table = init_table(table_name)
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
    except ClientError as dynamodb_error:
        print(f'\n Error while reading from table {table_name} : \n {dynamodb_error.response}')
        raise Exception('Exception encountered and run aborted!.')
    except Exception:
        raise Exception('Exception while reading data from table.')


def write_into_table(items, table_name):
    "Writes items/records into DynamoDB table"
    try:
        table = init_table(table_name)
        with table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)
        print(f"Added today's records successfully into DynamoDB table {table_name}!")
    except ClientError as dynamodb_error:
        print(f'\n Error while writing into table {table_name} :\n {dynamodb_error.response}')
    except Exception as error:
        print(f'Exception while inserting data into {table_name} table :\n {error}')
