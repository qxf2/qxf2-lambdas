"""
Calculate and store the delta values for the docker stats collected.
 - DynamoDB table format being:
   date, container_name, pulls.
Note: delta is the change per day on collected stats.
This script is expected to run every night.
"""
import datetime
import json
import streams_common_functions as scf
import conf as conf

def calculate_deltas(url):
    "Calculates the deltas for the repo stats."
    deltas = [] # list of dicts
    yesterday = (datetime.datetime.now()-datetime.timedelta(1)).strftime('%d-%b-%Y')
    today = datetime.datetime.now().strftime('%d-%b-%Y')
    yesterday_docker_stats = scf.read_db(url, conf.DOCKER_STATS_TABLE_NAME, yesterday)
    today_docker_stats = scf.read_db(url, conf.DOCKER_STATS_TABLE_NAME, today)
    for (t_stats, y_stats) in zip(today_docker_stats, yesterday_docker_stats):
        deltas.append({'date': t_stats['date'], 'image_name': t_stats['image_name'],\
                        'delta_pulls': t_stats['pulls']-y_stats['pulls']\
                     })
    return deltas

def store_deltas(url):
    "Stores the deltas of Docker Hub stats into DynamoDB."
    docker_deltas = calculate_deltas(url)
    scf.write_into_db(docker_deltas, conf.DOCKER_DELTAS_TABLE_NAME)



def handler(event, context):
    store_deltas(conf.DOCKER_HUB_URL)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Docker deltas running properly",
            # "location": ip.text.replace("\n", "")
        }),
    }
