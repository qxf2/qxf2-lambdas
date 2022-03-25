"""
Collect and store the GitHub stats for all Qxf2 repositories.
 - DynamoDB table format being:
   date, repo_name, stars, forks, clones, visitors.
This script is meant to be run everyday.
"""
import boto3
import datetime
import os
import time
from github import Github
import conf

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

def prepare_substreams(date, repos):
    "Prepare substream data by taking all repo info"
    substreams = [] # List of dicts
    for repo in repos:
        substreams.append({'date':date,\
                        'repo_name':repo})
    return substreams

def prepare_stats(date, all_repos):
    "Prepare stats data by taking all repo info"
    stats = [] #list of dicts
    github_obj = get_github_instance()
    for repo in all_repos:
        repo_obj = github_obj.get_repo(repo)
        stars = repo_obj.stargazers_count
        forks = repo_obj.forks
        visitor_stats = repo_obj.get_views_traffic()
        unique_visitors = visitor_stats.get('uniques', 0)
        clone_stats = repo_obj.get_clones_traffic()
        unique_clones = clone_stats.get('uniques', 0)
        stats.append({'date':date, 'repo_name':repo, 'stars':stars,\
            'forks':forks, 'clones':unique_clones, 'visitors':unique_visitors})
    return stats

def get_github_instance():
    "Returns a GitHub instance."
    github_obj = Github(os.environ["ACCESS_KEY"])
    return github_obj

def get_all_repos():
    "Gets all repos for the given username from GitHub."
    github_obj = get_github_instance()
    user = github_obj.get_user(os.environ["GITHUB_USER"])
    all_repos = []
    repos = user.get_repos('all')
    for repo in repos:
        if conf.GITHUB_USER + '/' in repo.full_name:
            all_repos.append(repo.full_name)
    return all_repos


def handler(event, context):
    "handler is the main lambda function from where execution will start"
    for retry_count in range(conf.RETRIES_COUNT):
        try:
            print(f'Retry attempt : {retry_count}')
            all_repos = get_all_repos()
            print("Fetched all GitHub repos!")
            current_date = datetime.datetime.now().strftime('%d-%b-%Y')
            substreams_data = prepare_substreams(current_date, all_repos)
            stats_data = prepare_stats(current_date, all_repos)
            print("Fetched stats for all GitHub repos!")
            message1 = write_into_table(substreams_data, conf.GITHUB_SUBSTREAMS_TABLE)
            message2 = write_into_table(stats_data, conf.GITHUB_STATS_TABLE)
            if message1 == 'data collected in github_substreams table' and message2 == 'data collected in github_stats table':
                return "github stats collected successfully"
            else:
                return "Error while writing into dynamodb table"
            break
        except Exception as error:
            print(f'Exception : {error}')
            time.sleep(10)
            continue
