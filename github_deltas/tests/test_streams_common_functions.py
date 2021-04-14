"""
testing working behavior of all the functions of
streams_common_functions in terms of different
input data
"""

import os
import sys
import pytest
from moto import mock_dynamodb2
from input_data import output_substreams,reading_substream,key,handler_substreams,github_stats,substreams,reading_message,table,data,message
import boto3
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streams_common_functions

@pytest.mark.parametrize('substreams,key,expected_output',[(output_substreams['single_data'],key,handler_substreams['single_data'])])
def test_extract_substream_names(substreams,key,expected_output):
    "function to test whether we are getting right sort of subtsream data"
    actual_output = streams_common_functions.extract_substream_names(substreams,key)
    assert expected_output ==actual_output

@pytest.mark.parametrize('substreams,output',[(output_substreams['single_data'],reading_substream)])
@mock_dynamodb2
def test_read_substreams(substreams,output):
    "test function to test writing of data into the given dynamodb table"
    dynamodb = boto3.resource('dynamodb', 'ap-south-1')
    table_name = 'github_test'
    table = dynamodb.create_table(
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
    with table.batch_writer() as batch:
        for item in substreams:
            batch.put_item(Item=item)
    actual_output = output
    expected_output = streams_common_functions.read_substreams(table_name,substreams[0]['date'])
    assert actual_output == expected_output

@pytest.mark.parametrize('data,substreams,output',
                         [(github_stats['single_stats'],
                          substreams['single_substream'],
                          reading_message['success'])])
@mock_dynamodb2
def test_read_github_table(data,substreams,output):
    "test function to test writing of data into the given dynamodb table"
    dynamodb = boto3.resource('dynamodb', 'ap-south-1')
    table_name = 'test'
    table = dynamodb.create_table(
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
    with table.batch_writer() as batch:
        for item in data:
            batch.put_item(Item=item)
    actual_output = output
    expected_output = streams_common_functions.read_github_table(table_name,data[0]['date'],substreams)
    assert actual_output == expected_output

@pytest.mark.parametrize('data,output',[(data['valid'],message['writing_success']),
                                        (data['date_not_present'],message['writing_failure'])])
@mock_dynamodb2
def test_write_into_table(data,output):
    "test function to test writing of data into the given dynamodb table"
    dynamodb = boto3.resource('dynamodb', 'ap-south-1')
    table_name = 'test'
    table = dynamodb.create_table(
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
