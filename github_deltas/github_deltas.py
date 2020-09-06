"""
Calculate and store the delta values for the GitHub stats collected.
 - DynamoDB table format being:
   date, repo_name, delta_stars, delta_forks, delta_clones, delta_visitors.
Note: delta is the change per day on collected stats.
"""
import datetime
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import conf as cf
import streams_common_functions as scf

def extract_new_substreams(current_day_substreams, previous_day_substreams):
    "Returns new substreams added, during the current day."
    new_substreams = list(set(current_day_substreams)-set(previous_day_substreams))
    return new_substreams

def amend_yesterday_repo_stats(yesterday, current_day_substreams,\
                             new_substreams, yesterday_repos_stats):
    "Inserts previous day stats as 0 for newly added repos."
    repo_index = [index for index, repo in enumerate(current_day_substreams)\
                    if repo in set(new_substreams)]
    for index, substream in zip(repo_index, new_substreams):
        yesterday_repos_stats.insert(index, {'date':yesterday, 'repo_name':substream,\
                                'stars':0, 'forks':0,\
                                'clones':0, 'visitors':0})
    return yesterday_repos_stats

def calculate_repo_deltas():
    "Calculates the deltas for the repo stats."
    deltas = [] # list of dicts
    yesterday = (datetime.datetime.now()-datetime.timedelta(1)).strftime('%d-%b-%Y')
    today = datetime.datetime.now().strftime('%d-%b-%Y')
    previous_day_substreams = scf.read_substreams(cf.GITHUB_SUBSTREAMS_TABLE, yesterday)
    current_day_substreams = scf.read_substreams(cf.GITHUB_SUBSTREAMS_TABLE, today)
    yesterday_repos_stats = scf.read_github_table(\
                cf.GITHUB_STATS_TABLE, yesterday, previous_day_substreams)
    today_repos_stats = scf.read_github_table(\
                cf.GITHUB_STATS_TABLE, today, current_day_substreams)
    if len(current_day_substreams) > len(previous_day_substreams):
        new_substreams = extract_new_substreams(current_day_substreams, previous_day_substreams)
        yesterday_repos_stats = amend_yesterday_repo_stats(yesterday, current_day_substreams,\
                                new_substreams, yesterday_repos_stats)
    for (t_stats, y_stats) in zip(today_repos_stats, yesterday_repos_stats):
        deltas.append({'date': t_stats['date'], 'repo_name': t_stats['repo_name'],\
                        'delta_stars': int(t_stats['stars'])-int(y_stats['stars']),\
                        'delta_forks': int(t_stats['forks'])-int(y_stats['forks']),\
                        'delta_clones': t_stats['clones'],\
                        'delta_visitors': t_stats['visitors']})
    store_repo_deltas(deltas)

def store_repo_deltas(repos_deltas):
    "Stores the deltas of GitHub repos stats into DynamoDB."
    scf.write_into_table(repos_deltas, cf.GITHUB_DELTAS_TABLE)

def handler(event, context):
    calculate_repo_deltas()
    print("Added Github deltas successfully!!!")
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "GitHub deltas running properly",
        }),
    }
