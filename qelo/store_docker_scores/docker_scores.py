"""
Lambda function to store the Docker substreams scores into DynamoDB every night.
"""
import datetime
from decimal import Decimal
import docker_conf as dc
import dynamodb_functions as df

def get_deltas_sum(substreams_deltas):
    "Returns sum of all deltas for the Docker substreams."
    delta_pulls_sum = 0
    for substream_deltas in substreams_deltas:
        delta_pulls_sum = delta_pulls_sum + int(substream_deltas['delta_pulls'])
    return delta_pulls_sum

def calculate_substreams_scores():
    "Calculates the scores for all Docker Hub images/sub-streams."
    substreams_scores = [] # list of dicts.
    today = datetime.datetime.now().strftime('%d-%b-%Y')
    # Get deltas of all Docker Hub sub-streams for the current day.
    current_day_substreams = df.read_substreams(dc.DOCKER_SUBSTREAMS_TABLE, today)
    current_day_substreams_deltas = df.read_docker_table(dc.DOCKER_DELTAS_TABLE, today,\
                                current_day_substreams)
    # Get the sum of all substreams deltas.
    delta_pulls_sum = get_deltas_sum(current_day_substreams_deltas)
    for substream_deltas in current_day_substreams_deltas:
        if delta_pulls_sum == 0:
            substreams_scores.append({'date': substream_deltas['date'],\
                                    'image_name': substream_deltas['image_name'],\
                                    'image_score': Decimal(0)})
        else:
            substreams_scores.append({'date': substream_deltas['date'],\
                                    'image_name': substream_deltas['image_name'],\
                                    'image_score': Decimal(str(round(\
                                    int(substream_deltas['delta_pulls'])/delta_pulls_sum\
                                    , 4)))})
    return substreams_scores

def store_substreams_scores():
    "Stores the Docker Hub sub-stream scores into DynamoDB."
    substreams_scores = []
    substreams_scores = calculate_substreams_scores()
    df.write_into_table(substreams_scores, dc.DOCKER_SCORES_TABLE)

def lambda_handler(event, context):
    "Lambda entry point."
    store_substreams_scores()
    return "Stored current day Docker substreams scores, successfully into DynamoDB."
