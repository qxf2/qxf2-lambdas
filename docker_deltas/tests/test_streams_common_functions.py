"""
testing all the functions of streams_common_functions
are working good in terms of different input situation.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unittest.mock import patch
from moto import mock_dynamodb2
import boto3
import pytest
import conf
import streams_common_functions
from input_data import *

@pytest.mark.parametrize('substreams,key,expected_output',
                         [(output_substreams['single_data'],key,
                          handler_substreams['single_data'])])
def test_extract_substream_names(substreams,key,expected_output):
    "testing could we extract right substream from the given data or not"
    actual_output = streams_common_functions.extract_substream_names(substreams,key)
    assert expected_output == actual_output

@pytest.mark.parametrize('substreams,output',
                         [(output_substreams['single_data'],substreams['single_substream'])])
@mock_dynamodb2
def test_read_substreams(substreams,output):
    "testing reading of substream data from the given dynamodb table"
    dynamodb = boto3.resource('dynamodb', 'ap-south-1')
    table_name = 'test'
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': 'date',
             'KeyType': 'HASH'},
            {'AttributeName': 'image_name',
             'KeyType': 'RANGE'},
        ],
        AttributeDefinitions=[
            {'AttributeName': 'date',
             'AttributeType': 'S'},
            {'AttributeName': 'image_name',
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

    expected_output = output
    actual_output = streams_common_functions.read_substreams(table_name,substreams[0]['date'])
    assert actual_output == expected_output

@pytest.mark.parametrize('data,substreams,output',
                         [(docker_stats['single_stats'],
                          substreams['single_substream'],
                          reading_message['success'])])
@mock_dynamodb2
def test_read_docker_table(data,substreams,output):
    "testing reading of stats data from the given dynamodb table"
    dynamodb = boto3.resource('dynamodb', 'ap-south-1')
    table_name = 'test'
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': 'date',
             'KeyType': 'HASH'},
            {'AttributeName': 'image_name',
             'KeyType': 'RANGE'},
        ],
        AttributeDefinitions=[
            {'AttributeName': 'date',
             'AttributeType': 'S'},
            {'AttributeName': 'image_name',
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

    expected_output = output
    actual_output = streams_common_functions.read_docker_table(table_name,data[0]['date'],substreams)
    assert actual_output == expected_output

@pytest.mark.parametrize('data,output',[(data['valid'],message['writing_success']),
                                        (data['date_not_present'],message['writing_failure'])])
@mock_dynamodb2
def test_write_into_table(data,output):
    "testing writing of data into the given dynamodb table"
    dynamodb = boto3.resource('dynamodb', 'ap-south-1')
    table_name = 'test'
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': 'date',
             'KeyType': 'HASH'},
            {'AttributeName': 'image_name',
             'KeyType': 'RANGE'},
        ],
        AttributeDefinitions=[
            {'AttributeName': 'date',
             'AttributeType': 'S'},
            {'AttributeName': 'image_name',
             'AttributeType': 'S'},
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    expected_output = output.format(table_name)
    actual_output = streams_common_functions.write_into_table(data,table_name)
    assert actual_output == expected_output
