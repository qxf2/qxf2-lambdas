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

def build_report_requests(view_id, date):
    "Defines the reportRequests for each webapps sub-stream and returns the JSON."
    metrics_list = ['ga:users']
    body = {'reportRequests': [{\
            'viewId': view_id,\
            'dateRanges': [{'startDate': date, 'endDate': date}],\
            'metrics': [{'expression': metric} for metric in metrics_list]}]}
    return body

def normalize_response(response):
    "Parses the Google Analytics API response to extract the users count for the webapp."
    for report in response.get('reports', []):
        data = report.get('data', {})
        totals = data.get('totals', [])
    for total in totals:
        values = total['values']
        user_count = values[0]
    return user_count

def get_webapps_substreams():
    "Fetches the webapps defined in the JSON."
    root_dir = os.path.dirname(os.path.abspath(__file__))
    webapps_substreams_json = os.path.join(root_dir, 'conf', 'webapps_conf.json')
    with open(webapps_substreams_json) as file:
        substreams = json.load(file)
    return substreams

def get_webapps_stats():
    "Returns the stats for every configured webapps."
    stats = []
    yesterday_date = (datetime.datetime.now()-datetime.timedelta(1)).strftime('%Y-%m-%d')
    all_apps = get_webapps_substreams()
    all_apps = all_apps.get('webapps', [])
    store_substreams(yesterday_date, all_apps)
    for web_app in all_apps:
        # Build the JSON for the reportRequests.
        report_requests_body = build_report_requests(web_app['view_id'], yesterday_date)
        # Get the API response for the defined reportRequests.
        api_response = af.get_api_response(report_requests_body)
        # Extract web app users count from the Google Analytics API reponse.
        users = normalize_response(api_response)
        # Build the web app stats.
        stats.append({'date':yesterday_date,\
                      'webapp_name':web_app['app_name'],\
                      'users_count':users
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
