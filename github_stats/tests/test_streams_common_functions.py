"""
testing working behavior of all the functions of
streams_common_functions in terms of different
input data
"""
import os
import sys
import pytest
from moto import mock_dynamodb2
import boto3
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from input_data import stats,message
import streams_common_functions

@pytest.mark.parametrize('data,output',[(stats['single'],message['success']),
                                        (stats['invalid'],message['failure'])])
@mock_dynamodb2
def test_write_into_table(data,output):
    "testing writing of data into the given dynamodb table"
    dynamodb = boto3.resource('dynamodb', 'ap-south-1')
    table_name = 'test'
    dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': 'date',
             'KeyType': 'HASH'},
            {'AttributeName': 'repo_name',
             'KeyType': 'RANGE'},
        ],
        AttributeDefinitions=[
            {'AttributeName': 'date',
             'AttributeType': 'S'},
            {'AttributeName': 'repo_name',
             'AttributeType': 'S'},
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    actual_output = output.format(table_name)
    expected_output = streams_common_functions.write_into_table(data,table_name)
    assert actual_output == expected_output
