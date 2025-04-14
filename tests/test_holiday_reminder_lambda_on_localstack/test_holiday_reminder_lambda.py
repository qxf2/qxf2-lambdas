#test_holiday_reminder_lambda.py

"""
Test Lambda on the LocalStack:
- Deploy Lambda along with its dependencies
- Run test
- Delete Lambda
"""
import time
from unittest import TestCase
import testutils

class HolidayReminderTest(TestCase):
    "Test to verify Lambda response"

    @classmethod
    def setup_class(cls):
        "Create SQS and lambda"
        print('\nCreating a SQS')
        testutils.create_queue('test-queue')
        print('\nCreating a holiday_reminder')
        testutils.create_lambda('holiday_reminder')
        cls.wait_for_function_active('holiday_reminder')

    @classmethod
    def teardown_class(cls):
        "Delete the Lambda, SQS  and teardown the session"
        print('\nDeleting the holiday_reminder')
        testutils.delete_lambda('holiday_reminder')
        print('\nDeleting the SQS test queue')
        queue_url = testutils.get_queue_url('test-queue')
        testutils.delete_queue(queue_url)

    @classmethod
    def wait_for_function_active(cls, function_name):
        "Wait till Lambda is up and active"
        lambda_client = testutils.get_lambda_client()
        while True:
            response = lambda_client.get_function(FunctionName=function_name)
            function_state = response['Configuration']['State']

            if function_state == 'Active':
                break

            time.sleep(1)  # Wait for 1 second before checking again

    def test_that_lambda_returns_upcoming_holiday(self):
        "Trigger and test Lambda's received message"
        print('\nInvoking the Lambda and verifying return message')
        event = {
            "key": "value"
        }

        # Invoke the Lambda function locally using LocalStack
        response = testutils.invoke_function_and_get_upcoming_holiday('holiday_reminder', event)

        # Check if the response contains the expected message
        self.assertIn("inform the client about it", response['msg'])
