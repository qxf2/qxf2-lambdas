"""
Lambda to calculate and store the sub-streams scores for webapps.
"""
import datetime
import os
import sys
from decimal import Decimal
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import dynamodb_functions as df

def get_deltas_sum(substreams_deltas):
    "Returns sum of all deltas for the substreams."
    delta_users_sum = 0
    for substream_deltas in substreams_deltas:
        delta_users_sum = delta_users_sum + int(substream_deltas['users_count'])
    return delta_users_sum

def calculate_substreams_scores():
    "Calculates the webapps substreams scores."
    substreams_scores = []
    yesterday = (datetime.datetime.now()-datetime.timedelta(1)).strftime('%Y-%m-%d')
    # Get yesterday's deltas for all webapp sub-streams.
    yesterday_substreams = df.read_substreams(os.environ['WEBAPP_SUBSTREAMS_TABLE'], yesterday)
    yesterday_substreams_deltas = df.read_webapps_table(os.environ['WEBAPP_DELTAS_TABLE'], \
                                    yesterday, yesterday_substreams)
    delta_users_sum = get_deltas_sum(yesterday_substreams_deltas)
    for substream_deltas in yesterday_substreams_deltas:
        if delta_users_sum == 0:
            substreams_scores.append({'date':substream_deltas['date'],\
                                'webapp_name':substream_deltas['webapp_name'],\
                                'webapp_score':Decimal(0)})
        else:
            substreams_scores.append({'date':substream_deltas['date'],\
                                'webapp_name':substream_deltas['webapp_name'],\
                                'webapp_score':Decimal(str(round(\
                                int(substream_deltas['users_count'])/delta_users_sum, 4)))})
    store_substreams_scores(substreams_scores)

def store_substreams_scores(substreams_scores):
    "Stores the webapps sub-streams scores into DynamoDB."
    df.write_into_table(substreams_scores, os.environ['WEBAPP_SCORES_TABLE'])

def lambda_handler(event, context):
    "Lambda entry point."
    calculate_substreams_scores()
    return "Calculated and stored yesterday's webapps scores, successfully into DynamoDB."
