"""
Module to contain functions related to accessing the Google Analytics Data API v1
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
            DateRange, Metric, RunReportRequest)

def get_data_api_response(property_id, extraction_date):
    "Builds the API request and fetches total Users count from GA4 properties"
    try:
        client = BetaAnalyticsDataClient()
        request = RunReportRequest(
            property=f"properties/{property_id}",
            metrics=[Metric(name="totalUsers")],
            date_ranges=[DateRange(start_date=extraction_date, end_date=extraction_date)],
        )
        response = client.run_report(request)
    except Exception as error:
        print(f'\n Python says: {error}')
        raise Exception('\n Exception while accessing the API.') from error
    return response
