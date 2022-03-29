"""
Collect and store GitHub stats for all Qxf2 repositories
 - DynamoDB table format being:
   date, repo_name, stars, forks, clones, visitors
This script is meant to be run daily at 11pm UST (ie 4.30am IST)
"""
from datetime import datetime
import os
import time
from github import Github
import dynamodb_functions

def get_github_instance():
    "Returns a GitHub instance"
    github_obj = Github(os.environ["GITHUB_ACCESS_KEY"])
    return github_obj

def get_all_repos():
    "Gets all repos for the given username from GitHub"
    github_obj = get_github_instance()
    user = github_obj.get_user(os.environ["GITHUB_USER"])
    all_repos = []
    repos = user.get_repos('all')
    for repo in repos:
        if os.environ["GITHUB_USER"] + '/' in repo.full_name:
            all_repos.append(repo.full_name)
    return all_repos

def prepare_substreams(date, repos):
    "Prepare substream data by taking all repo info"
    substreams = [] # List of dicts
    for repo in repos:
        substreams.append({'date':date,\
                        'repo_name':repo})
    return substreams

def prepare_stats(date, repos):
    "Prepare stats data by taking all repo info"
    stats = [] #list of dicts
    github_obj = get_github_instance()
    for repo in repos:
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

def lambda_handler(event, context):
    "Lambda entry point"
    for retry_count in range(int(os.environ["RETRIES_COUNT"])):
        try:
            print(f'Retry attempt : {retry_count}')
            all_repos = get_all_repos()
            print("Fetched all GitHub repos!")
            current_date = datetime.now().strftime('%d-%b-%Y')
            substreams_data = prepare_substreams(current_date, all_repos)
            stats_data = prepare_stats(current_date, all_repos)
            print("Fetched stats for all GitHub repos!")
            dynamodb_functions.write_into_table(substreams_data,
                                            os.environ["GITHUB_SUBSTREAMS_TABLE"])
            dynamodb_functions.write_into_table(stats_data,
                                            os.environ["GITHUB_STATS_TABLE"])
            break
        except Exception as error:
            print(f'Exception : {error}')
            time.sleep(10)
            continue
