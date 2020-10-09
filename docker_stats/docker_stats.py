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

def store_substreams(date,images):
    "Stores the GitHub repos/substreams."
    substreams = [] # List of dicts
    for image in images:
        substreams.append({'date':date,'image_name':image['name']})
    return substreams

def store_image_stats(date,stats_data):
    "Stores pulls count for all docker images."
    stats = []#list of dicts
    for data in stats_data:
        stats.append({'date':date,\
                    'image_name':data['name'], 'pulls':data['pull_count']})
    return stats

def handler(event, context):
    "handler function is the lambda function, from where execution starts"
    all_data = scf.get_current_docker_data(cf.DOCKER_HUB_URL)
    print("current docker data collected:)")
    date = datetime.datetime.now().strftime('%d-%b-%Y')
    substreams = store_substreams(date,all_data)
    stats = store_image_stats(date,all_data)
    print("data prepared for writing!!!")
    message1 = scf.write_into_table(substreams, cf.DOCKER_SUBSTREAMS_TABLE)
    message2 = scf.write_into_table(stats, cf.DOCKER_STATS_TABLE)
    if message1 == 'data collected in docker_substreams table' and \
       message2 == 'data collected in docker_stats table':
        return "docker stats collected successfully"
    else:
        return "Error while writing into dynamodb table"
