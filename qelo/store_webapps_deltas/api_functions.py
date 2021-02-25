"""
Module to contain functions related to accessing the Google Analytics Reporting API v4.
"""
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import httplib2
from google.oauth2 import service_account
from googleapiclient.discovery import build

def get_analytics_reporting_service_object():
    "Initializes and returns an Analytics Reporting API V4 service object."
    scope = ['https://www.googleapis.com/auth/analytics.readonly']
    credentials = service_account.Credentials.from_service_account_info(\
                                            json.loads(os.environ['API_CREDENTIALS']))
    scoped_credentials = credentials.with_scopes(scope)
    # Build the service object.
    analytics_obj = build('analyticsreporting', 'v4', credentials=scoped_credentials)
    # Returns an authorized Analytics Reporting API V4 service object.
    return analytics_obj

def get_api_response(body):
    "Gets the dimensions and metrics data as per the defined reportRequest."
    try:
        analytics_obj = get_analytics_reporting_service_object()
        return analytics_obj.reports().batchGet(body=body).execute()
    except httplib2.ServerNotFoundError as server_not_found:
        raise Exception('\n Intermittent connection issues with server. Re-run script.')\
                                                                    from server_not_found
    except Exception as error:
        print('\n Python says: {}'.format(error))
        raise Exception('\n Exception while accessing the API.') from error
