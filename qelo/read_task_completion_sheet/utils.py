"""
This module contains all the required methods for the lambda
"""
import calendar
import csv
import json
import os
import re
from datetime import date
from io import StringIO
import boto3
import gspread
import pandas as pd
from botocore.exceptions import ClientError
from google.oauth2 import service_account


def get_sheet():
    "Connect to Google Sheets and get the sheet"
    scope = ['https://www.googleapis.com/auth/drive']
    credentials = service_account.Credentials.from_service_account_info(\
                        json.loads(os.environ['API_CREDENTIALS']), scopes = scope)
    gspread_obj = gspread.authorize(credentials)
    gsheet = gspread_obj.open(os.environ['SHEET_NAME']).worksheet(os.environ['WORKSHEET_NAME'])
    return gsheet


def read_sheet():
    "Reads the spreadsheet into a dataframe"
    gsheet = get_sheet()
    spreadsheet_data = gsheet.get_all_values()
    headers = spreadsheet_data.pop(0)
    return spreadsheet_data, headers


def get_current_date_info():
    "Gets the current month and year info."
    current_date = date.today()
    current_month = current_date.strftime('%b')
    current_year = current_date.strftime('%Y')
    return current_month, current_year


def get_months():
    "Extracts month names in MMM format."
    month_names = []
    months = [calendar.month_name[i] for i in range(1, 13)]
    for _, month  in enumerate(months):
        month_names.append(month[0:3])
    return month_names


def filter_current_quarter_data(spreadsheet_data):
    "Filters the current quarter's data from the overall spreasheet data."
    data = []
    # Get current month and year.
    current_month, current_year = get_current_date_info()
    # Get the month names in MMM format.
    months = get_months()
    for index, sheet_data in enumerate(spreadsheet_data):
        # Search spreadsheet data and select those records that match the current quarter
        if re.search(r'Jan|Feb|Mar', current_month, re.IGNORECASE):
            if re.search(r'([0-9]{1,2}).(\b%s|%s|%s\b).(\b%s\b)'\
                        %(months[0], months[1], months[2], current_year),\
                        sheet_data[2], re.IGNORECASE):
                data.append(spreadsheet_data[index])
        elif re.search(r'Apr|May|Jun', current_month, re.IGNORECASE):
            if re.search(r'([0-9]{1,2}).(\b%s|%s|%s\b).(\b%s\b)'\
                    %(months[3], months[4], months[5], current_year),\
                    sheet_data[2], re.IGNORECASE):
                data.append(spreadsheet_data[index])
        elif re.search(r'Jul|Aug|Sep', current_month, re.IGNORECASE):
            if re.search(r'([0-9]{1,2}).(\b%s|%s|%s\b).(\b%s\b)'\
                    %(months[6], months[7], months[8], current_year),\
                    sheet_data[2], re.IGNORECASE):
                data.append(spreadsheet_data[index])
        elif re.search(r'Oct|Nov|Dec', current_month, re.IGNORECASE):
            if re.search(r'([0-9]{1,2}).(\b%s|%s|%s\b).(\b%s\b)'\
                    %(months[9], months[10], months[11], current_year),\
                    sheet_data[2], re.IGNORECASE):
                data.append(spreadsheet_data[index])
    return data


def to_csv(data, headers):
    "Reads the data into a csv"
    data = pd.DataFrame(data, columns=headers)
    csv_buffer = StringIO()
    data.to_csv(csv_buffer, index=False)
    return csv_buffer


def upload_to_s3(csv_buffer, filename, content):
    "Upload the data to S3 bucket"
    s3_resource = boto3.resource('s3')
    s3_resource.Object(os.environ['S3_BUCKET'], filename).put(Body=csv_buffer.getvalue())
    print(f"{content} backup of task completion data at {os.environ['S3_BUCKET']} S3 bucket, as {filename}")


def prepare_data(filename):
    "Prepare the data to transfer it to DynamoDB"
    s3_client = boto3.client('s3')
    csv_object = s3_client.get_object(Bucket=os.environ['S3_BUCKET'], Key=filename)
    csv_file = csv_object['Body'].read().decode('utf-8')
    data = csv_file.split("\n")
    return data


def init_table(table_name):
    "Initializes and returns the DynamoDB table resource."
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    return table


def initiate_migrate(row_data, table):
    "Initiates the process of migrating data from S3 to DynamoDB"
    with table.batch_writer() as batch:
        for email in row_data[4].split(','):
            batch.put_item(
                Item={
                    "TaskNo": int(row_data[0]),
                    "Task" :row_data[1],
                    "DateOfCompletion" :row_data[2],
                    "TrelloTicket" : row_data[3],
                    "Email":email.strip(),
                    "ArtifactLocation":row_data[5],
                    "Techs" : row_data[6],
                    "NextSteps":row_data[7],
                    "Level":row_data[8],
                    "Stream":row_data[9],
                    "Substream":row_data[10],
                    "Share":row_data[11]
                }
            )


def migrate_to_dynamodb(data):
    "Populate DynamoDB with complete sheet data"
    is_empty = False
    table = init_table(os.environ['TABLE_NAME'])
    if table.item_count == 0 :
        is_empty = True
        for row_data in  csv.reader(data[1:], quotechar='"',\
            delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True):
            if row_data:
                try:
                    initiate_migrate(row_data, table)
                except ClientError as dynamodb_error:
                    print(f"\n Error while migrating data into table {os.environ['TABLE_NAME']}: \n {dynamodb_error.response}")
                    raise Exception('Exception encountered and run aborted!.') from dynamodb_error
                except Exception as error:
                    raise Exception('Exception while migrating data into table.') from error
        print(f"Task completion data migrated to {os.environ['TABLE_NAME']} table in DynamoDB.")
    return is_empty


def initiate_update(row_data, table):
    "Initiates the updation of current quarter data into DynamoDB"
    for email in row_data[4].split(','):
        table.update_item(
            ExpressionAttributeNames= {"#lev":"Level", "#s":"Stream", "#sh":"Share"},
            ExpressionAttributeValues={
                ":att1":row_data[1], # Task attribute
                ":att2":row_data[2], # DateOfCompletion attribute
                ":att3":row_data[3], # TrelloTicket attribute
                ":att5":row_data[5], # ArtifactLocation attribute
                ":att6":row_data[6], # Techs attribute
                ":att7":row_data[7], # NextSteps attribute
                ":Level":row_data[8], # Level attribute
                ":Stream":row_data[9], # Stream attribute
                ":att10":row_data[10],# Substream attribute
                ":Share":row_data[11] # Share attribute
            },
            Key={
                "TaskNo": int(row_data[0]), #primary key
                "Email": email.strip(), #sort key
            },
            UpdateExpression="SET Task = :att1,\
                DateOfCompletion = :att2, TrelloTicket = :att3,\
                ArtifactLocation = :att5, Techs = :att6,\
                NextSteps = :att7, #lev = :Level, #s = :Stream,\
                Substream = :att10, #sh = :Share"
        )


def update_dynamodb(data):
    "Update the dynamodb with the current quarter data"
    table = init_table(os.environ['TABLE_NAME'])
    for row_data in  csv.reader(data[1:], quotechar='"',\
        delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True):
        if row_data:
            try:
                initiate_update(row_data, table)
            except ClientError as dynamodb_error:
                print(f"\n Error while updating data into table {os.environ['TABLE_NAME']}: \n {dynamodb_error.response}")
                raise Exception('Exception encountered and run aborted!.') from dynamodb_error
            except Exception as exception:
                print(f"Failed with exception {exception.__class__.__name__}")
                raise Exception('Exception while updating data into table.') from exception
    print(f"Updated {os.environ['TABLE_NAME']} table in DynamoDB with current quarters data.")
