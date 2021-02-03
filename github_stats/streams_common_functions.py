"""
Module to contain functions that are common across various streams:
- stats fetching scripts.
"""
import os
import sys
import boto3
from github import Github
import conf
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_github_instance():
    "Returns a GitHub instance."
    github_obj = Github(os.environ["ACCESS_KEY"])
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
        return 'data collected in {} table'.format(table_name)
    except Exception:
        return 'Exception while inserting data into table.'