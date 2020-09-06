"""
Collect and store the GitHub stats for all Qxf2 repositories.
 - DynamoDB table format being:
   date, repo_name, stars, forks, clones, visitors.
This script is meant to be run everyday.
"""
import json
import datetime
import conf as cf
import streams_common_functions as scf

def get_repo_stats(repo_name):
    "Gets stars, forks, unique clones, unique visitors for a repo."
    current_date = datetime.datetime.now().strftime('%d-%b-%Y')
    github_obj = scf.get_github_instance()
    repo = github_obj.get_repo(repo_name)
    stars = repo.stargazers_count
    forks = repo.forks
    visitor_stats = repo.get_views_traffic()
    unique_visitors = visitor_stats.get('uniques', 0)
    clone_stats = repo.get_clones_traffic()
    unique_clones = clone_stats.get('uniques', 0)
    return {'date':current_date, 'repo_name':repo_name, 'stars':stars,
            'forks':forks, 'clones':unique_clones, 'visitors':unique_visitors}

def store_repo_stats(username):
    "Stores the Github stats for all repos that the user owns."
    all_repos = scf.get_all_repos(username)
    stats_obj = [] #list of all github data
    substream_obj = [] #list of only substream data
    for repo in all_repos:
        repo_stats = get_repo_stats(repo)
        substream_stats = {'date':repo_stats['date'], 'repo_name':repo_stats['repo_name']}
        stats_obj.append(repo_stats)
        substream_obj.append(substream_stats)
    # Write the github stats into the github_stats DynamoDB table.
    scf.write_data_into_db(stats_obj, cf.GITHUB_STATS_TABLE_NAME)
    # Write the github substream stats into the github_subtreams DynamoDB table.
    scf.write_substream_into_db(substream_obj, cf.GITHUB_SUBSTREAM_TABLE_NAME)

def handler(event, context):
    "handler is the main lambda function from where execution will start"
    store_repo_stats(cf.GITHUB_USER)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "github_stats running properly",
        }),
    }
