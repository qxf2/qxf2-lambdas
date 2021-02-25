"""
Module to contain the DynamoDB operations related to QElo.
"""
import boto3
from botocore.exceptions import ClientError

def write_into_table(items, table_name):
    "Writes items/records into DynamoDB table."
    dynamodb = None
    # Initialize a DynamoDB table resource.
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
    try:
        with table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)
        print(f"\n Added yesterday's records successfully into DynamoDB table {table_name}.")
    except ClientError as dynamodb_error:
        print(f'\n Error while writing into table {table_name} : \n {dynamodb_error.response}')
        raise Exception('Exception encountered and run aborted!.') from dynamodb_error
    except Exception as error:
        raise Exception('Exception while inserting data into table.') from error
