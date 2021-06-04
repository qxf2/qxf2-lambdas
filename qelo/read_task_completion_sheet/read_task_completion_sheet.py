"""
This script is intended to backup R&D task completion data in S3 and DynamoDB, every Saturday.
"""
import os
import utils

def lambda_handler(event, context):
    "Lambda entry point"
    table_empty = False
    upload_status = 0
    # Read the spreadsheet
    spreadsheet_data, headers = utils.read_sheet()

    # Upload spreadsheet data to S3 bucket
    upload_status = utils.upload_to_s3(spreadsheet_data, headers, \
        os.environ['COMPLETE_SHEET_S3_KEY'], 'Complete')
    if upload_status == 1:
        utils.upload_to_s3(spreadsheet_data, headers, \
            os.environ['CURRENT_QUARTER_S3_KEY'], \
            'Current quarter data')

    # Store the complete spreadsheet data, if the DynamoDB table is empty
    table_empty = utils.migrate_to_dynamodb()

    # Update the DynamoDB with edits to current quarter data
    if table_empty is False:
        utils.update_dynamodb()

    return "Read task completion sheet and, populated S3 and Dynamodb"
