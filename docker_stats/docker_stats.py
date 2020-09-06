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
    substream_obj = []#list of dicts of substream
    current_date = datetime.datetime.now().strftime('%d-%b-%Y')
    all_data = scf.get_current_docker_data(url)
    for data in all_data['results']:
        stats_obj.append({'date':current_date,\
                    'image_name':data['name'], 'pulls':data['pull_count']})
        substream_obj.append({'date':current_date,'image_name':data['name']})
    # Write docker stats into a DB.
    scf.write_data_into_db(stats_obj, cf.DOCKER_STATS_TABLE_NAME)
    return substream_obj

def handler(event, context):
    "handler function is the lambda function, from where execution starts"
    substream_data = store_docker_stats(cf.DOCKER_HUB_URL)
    scf.write_substream_into_db(substream_data,cf.DOCKER_SUBSTREAM_TABLE_NAME)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "docker_stats running properly",
        }),
    }
