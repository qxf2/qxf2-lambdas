"""
Collect and store the Docker Hub stats for all Qxf2 docker containers.
 - DynamoDB table format being:
   date, container_name, pulls.
This script is expected to run every night.
"""
import json
import boto3
import datetime
import requests
import conf

def write_into_table(items, table_name):
    "Writes items/records into DynamoDB table."
    dynamodb = None
    # Initialise a DynomoDB table resource.
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
    try:
        with table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)
        print(f"Added today's records successfully into DynamoDB table {table_name}.")
        return 'data collected in {} table'.format(table_name)
    except Exception:
        return 'Exception while inserting data into {} table'.format(table_name)

def prepare_data(all_data):
    "Prepare data in proper form to collect into dynamodb table"
    stats,substreams,result = [],[],[]
    current_date = datetime.datetime.now().strftime('%d-%b-%Y')
    for image in all_data:
        substreams.append({'date':current_date,\
                    'image_name':image['name']})
    result.append(substreams)
    for data in all_data:
        stats.append({'date':current_date,\
                    'image_name':data['name'], 'pulls':data['pull_count']})
    result.append(stats)
    return result

def get_docker_image_data():
    "Gets the data from Docker Hub for all docker images."
    response = requests.get(conf.DOCKER_HUB_URL)
    result = response.json()
    return result['results']

def handler(event, context):
    "handler function is the lambda function, from where execution starts"
    all_data = get_docker_image_data()
    print("current docker data collected:)")
    substreams_data, stats_data = prepare_data(all_data)
    print("data prepared for writing!!!")
    message1 = write_into_table(substreams_data, conf.DOCKER_SUBSTREAMS_TABLE)
    message2 = write_into_table(stats_data, conf.DOCKER_STATS_TABLE)
    if message1 == 'data collected in docker_substreams table' and message2 == 'data collected in docker_stats table':
        return "docker stats collected successfully"
    else:
        return "Error while writing into dynamodb table"
