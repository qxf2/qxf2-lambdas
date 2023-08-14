"""
Lambda function to
- fetch previous day's web application stats/deltas from Google Analytics and
- store into DynamoDB daily.
Note: 1. To add a new webapp/sub-stream, append it to conf/webapps_conf.json file.
      2. Note: We are fetching yesterday's data (GMT) since we want what was there at
        the end of the day. So, the script is meant to run at 12:00am GMT (ie. 5:30am IST).
"""
import datetime
import json
import os
import sys
sys.path.append((os.path.dirname(os.path.abspath(__file__))))
import dynamodb_functions as df
import api_functions as af

def normalize_response(response):
    "Parses Google Analytics Data API v1 response and extracts total users count for web-app."
    user_count = 0
    for row in response.rows:
        user_count = row.metric_values[0].value
    return user_count

def get_webapps_substreams():
    "Fetches the webapps defined in the JSON."
    root_dir = os.path.dirname(os.path.abspath(__file__))
    webapps_substreams_json = os.path.join(root_dir, 'conf', 'webapps_conf.json')
    with open(webapps_substreams_json, encoding='utf-8') as file:
        substreams = json.load(file)
    return substreams

def get_webapps_stats():
    "Returns the stats for every configured webapps"
    stats = []
    yesterday_date = (datetime.datetime.now()-datetime.timedelta(1)).strftime('%Y-%m-%d')
    all_apps = get_webapps_substreams()
    all_apps = all_apps.get('webapps', [])
    store_substreams(yesterday_date, all_apps)
    for web_app in all_apps:
        api_response = af.get_data_api_response(web_app['property_id'], yesterday_date)
        users_count = normalize_response(api_response)
        # Build the web apps stats
        stats.append({'date':yesterday_date,\
                      'webapp_name':web_app['app_name'],\
                      'users_count':users_count
                      })
    store_webapp_stats_as_deltas(stats)

def store_substreams(date, web_apps):
    "Stores the webapp substreams."
    substreams = []
    for web_app in web_apps:
        substreams.append({'date':date,\
                        'webapp_name':web_app['app_name']})
    df.write_into_table(substreams, os.environ['WEBAPP_SUBSTREAMS_TABLE'])

def store_webapp_stats_as_deltas(stats):
    "Stores stats for every configured webapps as deltas"
    df.write_into_table(stats, os.environ['WEBAPP_DELTAS_TABLE'])

def lambda_handler(event, context):
    "Lambda entry point."
    get_webapps_stats()
    return "Stored yesterday's webapps stats/deltas, successfully into DynamoDB."
