"""
    Module to contain the DynamoDB operations related to QElo.
"""
import re
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

def extract_substream_names(substreams_data, key):
    "Extracts the name of substreams from the complete substreams data."
    substreams = [substream_data[key] for substream_data in substreams_data]
    return substreams

def read_substreams(table_name, date):
    "Retrieves substreams from the corresponding DynamoDB table."
    dynamodb = None
    # Initialise a DynomoDB table resource.
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
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
    except ClientError as dynamodb_error:
        print(f'\n Error while reading from table {table_name} : \n {dynamodb_error.response}')
        raise Exception('Exception encountered and run aborted!.')
    except Exception:
        raise Exception('Exception while reading data from table.')

def read_github_table(table_name, date, substreams):
    "Retrieves items that match the criterias, from corresponding GitHub DynamoDB table."
    dynamodb = None
    data = [] #list of dicts
    # Initialise a DynomoDB table resource.
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
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
    except ClientError as dynamodb_error:
        print(f'\n Error while reading from table {table_name} : \n {dynamodb_error.response}')
        raise Exception('Exception encountered and run aborted!.')
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
        print(f"\n Added today's records successfully into DynamoDB table {table_name}.")
    except ClientError as dynamodb_error:
        print(f'\n Error while writing into table {table_name} : \n {dynamodb_error.response}')
        raise Exception('Exception encountered and run aborted!.')
    except Exception:
        raise Exception('Exception while inserting data into table.')


























"""
Module to contain functions that are common across various streams:
- stats fetching scripts.
- score generation scripts.

import sys
import os
import boto3
import requests
from github import Github
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import conf as conf


def get_github_instance():
    "Returns a GitHub instance."
    github_obj = Github(conf.TOKEN)
    return github_obj

def get_all_repos():
    "Gets all repos for the given username from GitHub."
    github_obj = get_github_instance()
    user = github_obj.get_user(conf.GITHUB_USER)
    all_repos = []
    repos = user.get_repos('all')
    for repo in repos:
        if conf.GITHUB_USER + '/' in repo.full_name:
            all_repos.append(repo.full_name)
    return all_repos

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
    if table_name in (conf.GITHUB_DELTAS_TABLE):
        try:
            for repo in substreams_info:
                response = table.get_item(
                    Key={
                        'date':date,
                        'repo_name':repo
                    }
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
    if table_name in (conf.GITHUB_DELTAS_TABLE):
        try:
            with table.batch_writer() as batch:
                for repo_stats in info:
                    date = repo_stats['date']
                    repo_name = repo_stats['repo_name']
                    print("Adding record for {} on {} to DynamoDB table {}."\
                            .format(repo_name, date, table_name))
                    batch.put_item(Item=repo_stats)
        except Exception:
            raise Exception('Exception while inserting data into table.')
"""