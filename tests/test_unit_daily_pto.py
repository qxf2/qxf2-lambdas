"""
Code level test for Daily PTO lambda
"""
import os
import json
import pytest
from unittest.mock import patch, MagicMock

# Set the environment variable before importing daily_pto
MOCK_CLIENT_SECRET = json.dumps({
    "type": "service_account",
    "project_id": "mock-project",
    "private_key_id": "mock-private-key-id",
    "private_key": "-----BEGIN PRIVATE KEY-----\nmock\n-----END PRIVATE KEY-----\n",
    "client_email": "mock@mock-project.iam.gserviceaccount.com",
    "client_id": "mock-client-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/mock@mock-project.iam.gserviceaccount.com"
})

os.environ["client_secret_google_calendar"] = MOCK_CLIENT_SECRET
os.environ["MAIN_CHANNEL"] = "test_channel"

from daily_pto.daily_pto import fetch_pto_names, write_message, lambda_handler

@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables required by daily_pto.py."""
    with patch.dict(os.environ, {
        "client_secret_google_calendar": MOCK_CLIENT_SECRET,
        "MAIN_CHANNEL": "test_channel"
    }):
        yield

@patch("daily_pto.daily_pto.googleapiclient.discovery.build")
@patch("daily_pto.daily_pto.service_account.Credentials.from_service_account_info")
def test_main(mock_credentials, mock_build):
    "Test the main function that fetches PTO names."
    mock_credentials.return_value = MagicMock()

    # Mock Google Calendar API response
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    mock_service.calendarList().list().execute.return_value = {
        "items": [{"id": "test@qxf2.com"}]
    }
    mock_service.events().list().execute.return_value = {
        "items": [{"summary": "test@qxf2.com: PTO", 
                   "start": {"date": "2025-01-30"}, 
                   "organizer": {"email": "test@qxf2.com"}}]
    }

    pto_list = fetch_pto_names()
    assert pto_list == ["test"]

@patch("daily_pto.daily_pto.boto3.client")
def test_write_message(mock_boto3):
    "Test that write_message correctly sends an SQS message."
    mock_sqs = mock_boto3.return_value
    write_message("Test message", "test_channel")
    mock_sqs.send_message.assert_called_once_with(
        QueueUrl="https://sqs.ap-south-1.amazonaws.com/285993504765/skype-sender",
        MessageBody="{'msg': 'Test message', 'channel': 'test_channel'}"
    )

@patch("daily_pto.daily_pto.fetch_pto_names", return_value=["test"])
@patch("daily_pto.daily_pto.write_message")
def test_lambda_handler(mock_write_message, mock_main):
    "Test the Lambda handler function."
    event = {"channel": "test_channel"}
    context = {}

    lambda_handler(event, context)

    mock_main.assert_called_once()
    mock_write_message.assert_called_once_with("PTO today:\ntest", "test_channel")
