"""
Module to contain the DynamoDB functions.
"""
import boto3
from botocore.exceptions import ClientError

def init_table(table_name):
    "Initializes and returns the DynamoDB table resource"
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    return table

def write_into_table(items, table_name):
    "Writes items/records into DynamoDB table"
    table = init_table(table_name)
    try:
        with table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)
        print(f"Added today's records successfully into DynamoDB table {table_name}!")
    except ClientError as dynamodb_error:
        print(f'\n Error while writing into table {table_name} :\n {dynamodb_error.response}')
    except Exception as error:
        print(f'Exception while inserting data into {table_name} table :\n {error}')
