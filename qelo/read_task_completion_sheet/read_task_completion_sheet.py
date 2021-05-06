"""
This script is intended to update R&D task completion data in S3 and DynamoDB, every Saturday.
    - Read R&D task completion spreadsheet data.
    - Store the complete data and current quarter data in S3
    - Update DynamoDB with the current quarter data, if table is not empty
    - If empty, write the complete spreadsheet data into DynamoDB table
"""
import os
import utils

def lambda_handler(event, context):
    "Lambda entry point"
    table_empty = False
    spreadsheet_data, headers = utils.read_sheet()
    filtered_data = utils.filter_current_quarter_data(spreadsheet_data)

    #Read the data into a csv
    complete_data = utils.to_csv(spreadsheet_data, headers)
    current_quarter_data = utils.to_csv(filtered_data, headers)

    #Upload the csv files to s3 bucket
    utils.upload_to_s3(complete_data, os.environ['COMPLETE_SHEET_S3_KEY'])
    utils.upload_to_s3(current_quarter_data, os.environ['CURRENT_QUARTER_S3_KEY'])

    #Prepare the data to initiate transfer to DynamoDB
    prepared_complete_data = utils.prepare_data(os.environ['COMPLETE_SHEET_S3_KEY'])
    prepared_quarter_data = utils.prepare_data(os.environ['CURRENT_QUARTER_S3_KEY'])

    #Store the complete task completion spreadsheet data, if the DynamoDB table is empty
    table_empty = utils.migrate_to_dynamodb(prepared_complete_data)

    #Update the DynamoDB with edits to current quarter data
    if table_empty is False:
        utils.update_dynamodb(prepared_quarter_data)

    return "Read task completion sheet and populated S3 and Dynamodb"
