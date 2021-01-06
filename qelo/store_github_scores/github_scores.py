"""
Lambda function to store the GitHub substreams scores into DynamoDB every night.
"""
import datetime
from decimal import Decimal
import github_conf as gc
import dynamodb_functions as df

def get_deltas_sum(substreams_deltas):
    "Returns sum of all deltas for the substreams."
    delta_stars_sum = 0
    delta_forks_sum = 0
    delta_clones_sum = 0
    delta_visitors_sum = 0
    deltas_sum = []
    for substream_deltas in substreams_deltas:
        delta_stars_sum = delta_stars_sum + int(substream_deltas['delta_stars'])
        delta_forks_sum = delta_forks_sum + int(substream_deltas['delta_forks'])
        delta_clones_sum = delta_clones_sum + int(substream_deltas['delta_clones'])
        delta_visitors_sum = delta_visitors_sum + int(substream_deltas['delta_visitors'])
    deltas_sum.insert(0, delta_stars_sum)
    deltas_sum.insert(1, delta_forks_sum)
    deltas_sum.insert(2, delta_clones_sum)
    deltas_sum.insert(3, delta_visitors_sum)
    return deltas_sum

def get_stars_weight(today_substreams_deltas, delta_stars_sum):
    "Returns the stars weight for the current day for all GitHub sub-streams."
    stars_weight = []
    if delta_stars_sum <= 0:
        stars_weight = [0 for substream_deltas in today_substreams_deltas]
    else:
        stars_weight = [round((int(substream_deltas['delta_stars'])/delta_stars_sum), 4)\
                        for substream_deltas in today_substreams_deltas]
    return stars_weight

def get_forks_weight(today_substreams_deltas, delta_forks_sum):
    "Returns the forks weight for the current day for all GitHub sub-streams."
    forks_weight = []
    if  delta_forks_sum <= 0:
        forks_weight = [0 for substream_deltas in today_substreams_deltas]
    else:
        forks_weight = [round(int((substream_deltas['delta_forks'])/delta_forks_sum), 4)\
                        for substream_deltas in today_substreams_deltas]
    return forks_weight

def get_clones_weight(today_substreams_deltas, delta_clones_sum):
    "Returns the clones weight for the current day for all GitHub sub-streams."
    clones_weight = []
    if  delta_clones_sum == 0:
        clones_weight = [0 for substream_deltas in today_substreams_deltas]
    else:
        clones_weight = [round((int(substream_deltas['delta_clones'])/delta_clones_sum), 4)\
                         for substream_deltas in today_substreams_deltas]
    return clones_weight

def get_visitors_weight(today_substreams_deltas, delta_visitors_sum):
    "Returns the visitors weight for the current day for all GitHub sub-streams."
    visitors_weight = []
    if  delta_visitors_sum == 0:
        visitors_weight = [0 for substream_deltas in today_substreams_deltas]
    else:
        visitors_weight = [round((int(substream_deltas['delta_visitors'])/delta_visitors_sum), 4)\
                            for substream_deltas in today_substreams_deltas]
    return visitors_weight

def calculate_substreams_scores():
    "Calculates the scores for all GitHub repos/sub-streams."
    substreams_scores = [] # list of dicts.
    deltas_sum = []
    today = datetime.datetime.now().strftime('%d-%b-%Y')
    # Get current day deltas for all github sub-streams.
    current_day_substreams = df.read_substreams(gc.GITHUB_SUBSTREAMS_TABLE, today)
    current_day_substreams_deltas = df.read_github_table(gc.GITHUB_DELTAS_TABLE, today,\
                                                    current_day_substreams)
    # Get the sum of all substreams deltas.
    deltas_sum = get_deltas_sum(current_day_substreams_deltas)
    # Get the current day GitHub metric weights.
    stars_weight = get_stars_weight(current_day_substreams_deltas,\
                                    deltas_sum[0])
    forks_weight = get_forks_weight(current_day_substreams_deltas,\
                                    deltas_sum[1])
    clones_weight = get_clones_weight(current_day_substreams_deltas,\
                                    deltas_sum[2])
    visitors_weight = get_visitors_weight(current_day_substreams_deltas,\
                                    deltas_sum[3])
    # Calculate the current day GitHub sub-streams scores.
    for substream_deltas, repo_stars_weight, repo_forks_weight, \
        repo_clones_weight, repo_visitors_weight \
        in zip(current_day_substreams_deltas, stars_weight,\
            forks_weight, clones_weight, visitors_weight):
        substreams_scores.append({'date': substream_deltas['date'],\
                                'repo_name': substream_deltas['repo_name'],\
                                'repo_score': Decimal(str(round(0.25 * \
                                (repo_stars_weight\
                                + repo_forks_weight \
                                + repo_clones_weight \
                                + repo_visitors_weight), 4)))})
    return substreams_scores

def store_substreams_scores():
    "Stores the GitHub sub-stream scores into DynamoDB."
    substreams_scores = []
    substreams_scores = calculate_substreams_scores()
    df.write_into_table(substreams_scores, gc.GITHUB_SCORES_TABLE)

def lambda_handler(event, context):
    "Lambda entry point."
    store_substreams_scores()
    return "Stored current day GitHub substreams scores, successfully into DynamoDB."
