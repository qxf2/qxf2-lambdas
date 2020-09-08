"""
Calculate and store the delta values for the docker stats collected.
 - DynamoDB table format being:
   date, image_name, delta_pulls.
Note: delta is the change per day on collected stats.
"""
import datetime
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import conf
import streams_common_functions as common_func

def amend_yesterday_images_stats(yesterday, current_day_substreams,\
                             new_substreams, yesterday_images_stats):
    "Inserts previous day pulls count as 0 for newly added Docker images."

    repo_index = [index for index, repo in enumerate(current_day_substreams)\
                    if repo in set(new_substreams)]
    for index, substream in zip(repo_index, new_substreams):
        yesterday_images_stats.insert(index, {'date':yesterday, 'image_name':substream,\
                                'pulls':0})
    return yesterday_images_stats

def extract_new_substreams(current_day_substreams, previous_day_substreams):
    "Returns new substreams added, during the current day."
    new_substreams = list(set(current_day_substreams)-set(previous_day_substreams))
    return new_substreams

def calculate_image_deltas():
    "Calculates the deltas for the docker image stats."
    deltas = [] # list of dicts
    yesterday = (datetime.datetime.now()-datetime.timedelta(1)).strftime('%d-%b-%Y')
    today = datetime.datetime.now().strftime('%d-%b-%Y')
    previous_day_substreams = common_func.read_substreams(conf.DOCKER_SUBSTREAMS_TABLE, yesterday)
    print(previous_day_substreams)
    current_day_substreams = common_func.read_substreams(conf.DOCKER_SUBSTREAMS_TABLE, today)
    print(current_day_substreams)
    yesterday_images_stats = common_func.read_docker_table(conf.DOCKER_STATS_TABLE, yesterday,\
                                    previous_day_substreams)
    print(yesterday_images_stats)
    today_images_stats = common_func.read_docker_table(conf.DOCKER_STATS_TABLE, today,\
                                    current_day_substreams)
    print(today_images_stats)
    if len(current_day_substreams) > len(previous_day_substreams):
        new_substreams = extract_new_substreams(current_day_substreams, previous_day_substreams)
        yesterday_images_stats = amend_yesterday_images_stats(yesterday, current_day_substreams,\
                                new_substreams, yesterday_images_stats)
    for (t_stats, y_stats) in zip(today_images_stats, yesterday_images_stats):
        deltas.append({'date': t_stats['date'], 'image_name': t_stats['image_name'],\
                        'delta_pulls': t_stats['pulls']-y_stats['pulls']\
                     })
    store_image_deltas(deltas)
    return current_day_substreams

def store_image_deltas(deltas):
    "Stores the deltas of docker image stats into DynamoDB."
    common_func.write_into_table(deltas, conf.DOCKER_DELTAS_TABLE)

def handler(event, context):
    "Lambda handler function for initiating the script"
    calculate_image_deltas()
    return {
        "body": json.dumps({
            "message": "Docker deltas running properly",
            # "location": ip.text.replace("\n", "")
        }),
    }
