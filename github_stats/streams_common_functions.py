"""
Module to contain functions that are common across various streams:
- stats fetching scripts.
"""
import os
import sys
import boto3
from github import Github
import conf as cf
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_github_instance():
    "Returns a GitHub instance."
    github_obj = Github(cf.TOKEN)
    return github_obj

def get_all_repos(username):
    "Gets all repos for the given username from GitHub."
    github_obj = get_github_instance()
    user = github_obj.get_user(username)
    all_repos = []
    repos = user.get_repos('all')
    for repo in repos:
        if username + '/' in repo.full_name:
            all_repos.append(repo.full_name)
    return all_repos

def write_into_db(info, table_name):
    "Writes info into DynamoDB table."
    dynamodb = None
    # Initialise a DynomoDB table resource.
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
    if table_name in cf.GITHUB_STATS_TABLE_NAME:
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
