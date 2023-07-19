"test utils for LocalStack tests"

import json
import os
import zipfile
import subprocess
import fnmatch
import boto3
import botocore

# Specify the paths and configuration
LAMBDA_ZIP='lambda_with_dependency.zip'
LAMBDA_FOLDER_PATH = '../url_filtering_lambda_rohini'
REQUIREMENTS_FILE_PATH = '../url_filtering_lambda_rohini/requirements.txt'
CONFIG = botocore.config.Config(retries={'max_attempts': 0})
LOCALSTACK_ENDPOINT = 'http://localhost.localstack.cloud:4566'

def get_lambda_client():
    "get lambda client"
    return boto3.client(
        'lambda',
        aws_access_key_id='test',
        aws_secret_access_key='test',
        region_name='us-east-1',
        endpoint_url= LOCALSTACK_ENDPOINT,
        config=CONFIG
    )

def get_sqs_client():
    "get SQS client"
    return boto3.client(
        'sqs', 
        aws_access_key_id='test',
        aws_secret_access_key='test',
        region_name='us-east-1',
        endpoint_url= LOCALSTACK_ENDPOINT)

def create_queue(queue_name):
    "Create a new SQS queue"
    sqs = get_sqs_client()
    response = sqs.create_queue(
        QueueName=queue_name,
        Attributes={
            'VisibilityTimeout': '300'  # Visibility timeout in seconds
        }
    )

    # Retrieve the URL of the created queue
    queue_url = response['QueueUrl']
    print("Queue URL:", queue_url)

def get_queue_url(queue_name):
    "Get the URL of an existing SQS queue"
    sqs = get_sqs_client()
    response = sqs.get_queue_url(QueueName=queue_name)
    queue_url = response['QueueUrl']
    print("Queue URL:", queue_url)

    return queue_url

def delete_queue(queue_url):
    "Delete the SQS queue"
    sqs = get_sqs_client()
    response = sqs.delete_queue(QueueUrl=queue_url)

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("Queue deleted successfully.")
    else:
        print("Failed to delete the queue.")

def create_zip_file_with_lambda_files_and_packages(lambda_zip, lambda_folder_path, temp_directory):
    "Create a zip file with lambda files and installed packages"
    with zipfile.ZipFile(lambda_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add the Lambda function code to the ZIP
        for root, dirs, files in os.walk(lambda_folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                if (not file_path.endswith('.zip') and not fnmatch.fnmatch(file_path, '*_pycache_*')
                    and not fnmatch.fnmatch(file_path, '*.pytest*')):
                    zipf.write(file_path, os.path.relpath(file_path, lambda_folder_path))

        # Add the installed packages to the ZIP at root
        for root, dirs, files in os.walk(temp_directory):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, temp_directory))

def delete_temp_file_and_its_content(temp_directory):
    "Delete the temporary directory and its contents"
    for root, dirs, files in os.walk(temp_directory, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            os.rmdir(dir_path)
    os.rmdir(temp_directory)

def create_lambda_zip(lambda_zip, lambda_folder_path, requirements_file_path):
    "Create a zip file to deploy Lambda along with its dependencies"
    # Create a temporary directory to install packages
    temp_directory = '../package'
    os.makedirs(temp_directory, exist_ok=True)

    # Install packages to the temporary directory
    subprocess.check_call(['pip', 'install', '-r', requirements_file_path, '-t', temp_directory])

    # Create a new ZIP file with Lambda files and installed packages
    create_zip_file_with_lambda_files_and_packages(lambda_zip, lambda_folder_path, temp_directory)

    # Remove the temporary directory and its contents
    delete_temp_file_and_its_content(temp_directory)

def create_lambda(function_name):
    "Create Lambda"
    lambda_client = get_lambda_client()
    create_lambda_zip(LAMBDA_ZIP, LAMBDA_FOLDER_PATH, REQUIREMENTS_FILE_PATH)
    with open(LAMBDA_ZIP, 'rb') as zip_file:
        zipped_code = zip_file.read()
    lambda_client.create_function(
        FunctionName=function_name,
        Runtime='python3.8',
        Role='arn:aws:iam::123456789012:role/test-role',
        Handler=function_name + '.lambda_handler',
        Code={"ZipFile": zipped_code},
        Timeout=180,
        Environment={
            'Variables': {
                'ETC_CHANNEL': 'dummy_chat@id.007',
                'Qxf2Bot_USER': 'dummy_user.id.006',
                'CHATGPT_API_KEY': os.environ.get('CHATGPT_API_KEY'),
                'CHATGPT_VERSION': os.environ.get('CHATGPT_VERSION'),
                'DEFAULT_CATEGORY': os.environ.get('DEFAULT_CATEGORY'),
                'API_KEY_VALUE': os.environ.get('API_KEY_VALUE'),
                'URL': os.environ.get('URL'),
                'SKYPE_SENDER_QUEUE_URL': get_queue_url('test-queue'),
                'employee_list': os.environ.get('employee_list'),
                'LOCALSTACK_ENV': 'true'
            }
        }
    )

def delete_lambda(function_name):
    "Delete Lambda"
    lambda_client = get_lambda_client()
    lambda_client.delete_function(
        FunctionName=function_name
    )
    os.remove(LAMBDA_ZIP)

def invoke_function_and_get_message(function_name, event):
    "trigger Lambda and return received message"
    lambda_client = get_lambda_client()

    # Convert the event message to JSON
    event_payload = json.dumps(event)

    # Invoke the Lambda function
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',
        Payload=event_payload
    )

    # Parse the response from the Lambda function
    response_payload = response['Payload'].read().decode('utf-8')
    response_data = json.loads(response_payload)
    print ("response data:", response_data)

    return response_data
    