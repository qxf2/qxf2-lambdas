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
#from oauth2client.service_account import ServiceAccountCredentials
import boto3
import gspread
import pandas as pd
from botocore.exceptions import ClientError
from google.oauth2 import service_account



def get_sheet():
    "Connect to Google Sheets and get the sheet"
    scope = ['https://www.googleapis.com/auth/drive']
    #credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scopes=scope)
    credentials = service_account.Credentials.from_service_account_info(\
                                        json.loads(os.environ['API_CREDENTIALS']))
    scoped_credentials = credentials.with_scopes(scope)
    gspread_obj = gspread.authorize(scoped_credentials)
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


def upload_to_s3(csv_buffer, filename):
    "Upload the data to s3 bucket"
    s3_resource = boto3.resource('s3')
    s3_resource.Object(os.environ['S3_BUCKET'], filename).put(Body=csv_buffer.getvalue())
    print(f"File uploaded to {os.environ['S3_BUCKET']}, as {filename}.")


def prepare_data(filename):
    "Prepare the data to transfer it to dynamodb"
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


def initiate_migrate(row_data):
    "initiates the process of migrating data from s3 to dynamodb"
    table = init_table(os.environ['TABLE_NAME'])
    with table.batch_writer() as batch:
        for email in row_data[4].split(','):
            batch.put_item(
                Item={
                    "TaskNo": int(row_data[0]),
                    "Task" :row_data[1],
                    "Date_of_Completion" :row_data[2],
                    "Trello_Ticket" : row_data[3],
                    "Email":email,
                    "Artificat_Location":row_data[5],
                    "Techs" : row_data[6],
                    "Next_Steps":row_data[7],
                    "Level_":row_data[8],
                    "Direct_Parent":row_data[9]
                }
            )


def migrate_to_dynamodb(data):
    "Populate dynamodb with complete sheet data"
    table = init_table(os.environ['TABLE_NAME'])
    if table.item_count == 0 :
        for row_data in  csv.reader(data[1:], quotechar='"',\
            delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True):
            if row_data:
                try:
                    initiate_migrate(row_data)
                except ClientError as error:
                    if error.response['Error']['Code'] == 'ConditionalCheckFailedException':
                        pass
        print(f"File migrated to Dynamodb, in {os.environ['TABLE_NAME']} table.")
        return True
    else:
        return False

def initiate_update(row_data):
    "initiates the updating of current quarter data in the dynamodb"
    table = init_table(os.environ['TABLE_NAME'])
    for email in row_data[4].split(','):
        table.update_item(
            Key={
                "TaskNo": int(row_data[0]), #primary key
                "Email": email, #sort key
            },
            UpdateExpression="SET Task = :att1,\
                Date_of_Completion = :att2, Trello_Ticket = :att3,\
                Artificat_Location= :att5, Techs = :att6,\
                Next_Steps= :att7, Level_= :att8, Direct_Parent= :att9",
            ExpressionAttributeValues={
                ":att1":row_data[1], # Task attribute
                ":att2":row_data[2], # Date_of_Completion attribute
                ":att3":row_data[3], # Trello_Ticket attribute
                ":att5":row_data[5], # Artificat_Location attribute
                ":att6":row_data[6], # Techs attribute
                ":att7":row_data[7], # Next_Steps attribute
                ":att8":row_data[8], # Level_ attribute
                ":att9":row_data[9]  # Direct_Parent attribute
            }
        )


def update_dynamodb(data):
    "Update the dynamodb with the current quarter data"
    for row_data in  csv.reader(data[1:], quotechar='"',\
        delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True):
        if row_data:
            try:
                initiate_update(row_data)
            except Exception as exception:
                print(f"Failed with exception {exception.__class__.__name__}")
    print(f"Updated {os.environ['TABLE_NAME']} table with current quarter data .")
