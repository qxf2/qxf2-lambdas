"""
Collect and store the GitHub stats for all Qxf2 repositories.
 - DynamoDB table format being:
   date, repo_name, stars, forks, clones, visitors.
This script is meant to be run everyday.
"""
import json
import datetime
import conf
import streams_common_functions as scf

def store_substreams(date, repos):
    "Stores the GitHub repos/substreams."
    substreams = [] # List of dicts
    for repo in repos:
        substreams.append({'date':date,\
                        'repo_name':repo})
    return substreams

def store_repo_stats(current_date, all_repos):
    "Stores the Github stats for all repos."
    stats = [] #list of dicts
    github_obj = scf.get_github_instance()
    for repo in all_repos:
        repo_obj = github_obj.get_repo(repo)
        stars = repo_obj.stargazers_count
        forks = repo_obj.forks
        visitor_stats = repo_obj.get_views_traffic()
        unique_visitors = visitor_stats.get('uniques', 0)
        clone_stats = repo_obj.get_clones_traffic()
        unique_clones = clone_stats.get('uniques', 0)
        stats.append({'date':current_date, 'repo_name':repo, 'stars':stars,\
            'forks':forks, 'clones':unique_clones, 'visitors':unique_visitors})
    return stats

def handler(event, context):
    "handler function is the lambda function, from where execution starts"
    all_data = scf.get_all_repos()
    print("current github data collected:)")
    current_date = datetime.datetime.now().strftime('%d-%b-%Y')
    substreams = store_substreams(current_date,all_data)
    stats = store_repo_stats(current_date,all_data)
    print("data prepared for writing!!!")
    message1 = scf.write_into_table(substreams, conf.GITHUB_SUBSTREAMS_TABLE)
    message2 = scf.write_into_table(stats, conf.GITHUB_STATS_TABLE)
    if message1 == 'data collected in github_substreams table' and message2 == 'data collected in github_stats table':
        return "github stats collected successfully"
    else:
        return "Error while writing into dynamodb table"
