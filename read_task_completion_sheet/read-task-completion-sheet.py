"""
This script is intended to update R&D task completion data in S3 and dynamodb, every saturday.
    - Read R&D task completion spreadsheet data.
    - Store the latest data in S3 and dynamodb
    - Updates the dynamodb with the current quarter data
"""
import json
import utils

def lambda_handler(event, context):
    "Lambda entry point"
    with open('config.json') as data_file:
        CONFIG = json.load(data_file)
    #Read the task completion sheet and filter current quarter data
    spreadsheet_data, headers = utils.read_sheet()
    filtered_data = utils.filter_current_quarter_data(spreadsheet_data)
    #Read the data into a csv
    complete_data = utils.to_csv(spreadsheet_data, headers)
    current_quarter_data = utils.to_csv(filtered_data, headers)
    #Upload the csv files to s3 bucket
    utils.upload_to_s3(complete_data, CONFIG['complete_sheet_s3_key'])
    utils.upload_to_s3(current_quarter_data, CONFIG['current_quarter_s3_key'])
    #Prepare the data to initiate transfer to dynamodb
    prepared_complete_data = utils.prepare_data(CONFIG['complete_sheet_s3_key'])
    prepared_quarter_data = utils.prepare_data(CONFIG['current_quarter_s3_key'])
    #Store the complete task compeltion sheet data if the dynamodb is empty
    utils.migrate_to_dynamodb(prepared_complete_data)
    #Update the dynamodb with edits to current quarter data
    utils.update_dynamodb(prepared_quarter_data)
    return "Read task completion sheet and populated dynamodb"
