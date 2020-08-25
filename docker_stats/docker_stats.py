"""
Collect and store the Docker Hub stats for all Qxf2 docker containers.
 - DynamoDB table format being:
   date, container_name, pulls.
This script is expected to run every night.
"""
import json
import datetime
import conf as cf
import streams_common_functions as scf

def store_docker_stats(url):
    "Stores today's docker pulls for all containers."
    stats_obj = []#list of dicts
    current_date = datetime.datetime.now().strftime('%d-%b-%Y')
    all_data = scf.get_current_docker_data(url)
    for data in all_data['results']:
        stats_obj.append({'date':current_date,\
                    'image_name':data['name'], 'pulls':data['pull_count']})
    # Write docker stats into a DB.
    scf.write_into_db(stats_obj, cf.DOCKER_STATS_TABLE_NAME)

def handler(event, context):
    "handler function is the lambda function, from where execution starts"
    store_docker_stats(cf.DOCKER_HUB_URL)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "docker_stats running properly",
        }),
    }
