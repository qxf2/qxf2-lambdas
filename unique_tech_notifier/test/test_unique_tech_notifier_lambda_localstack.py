"""
Test URL Filter Lambda on the LocalStack:
- Deploy Lambda along with its dependencies and SQS
- Run test
- Delete Lambda and SQS queue
"""
import time
from unittest import TestCase
import testutils as testutils
import unittest
from unique_tech_notifier import lambda_handler


class UrlFilterLambdaLocalStackTest(TestCase):
    "Deploy Lambda, SQS on LocalStack and run the test"
    @classmethod
    def setup_class(cls):
        "Create SQS and Lambda"
        print('\nCreating a SQS')
        testutils.create_queue('test-queue')
        print('\nCreating the Lambda')
        testutils.create_lambda('unique_tech_notifier')
        cls.wait_for_function_active('unique_tech_notifier')

    @classmethod
    def teardown_class(cls):
        "Delete the Lambda, SQS  and teardown the session"
        print('\nDeleting the Lambda')
        testutils.delete_lambda('unique_tech_notifier')
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

    def test_that_lambda_returns_unique_techs(self):
        "Test Lambda's received message"
        print('\nInvoking the Lambda and verifying return message')
        
        # Test case with unique techs learned
        event_with_unique_techs = {
            "channel": "main"
        }

        result_with_unique_techs = lambda_handler(event_with_unique_techs, None)

        self.assertIsNotNone(result_with_unique_techs)
        self.assertIn('unique_tech_message', result_with_unique_techs)
        self.assertIn('weekly_tech_message', result_with_unique_techs)

        unique_tech_message = result_with_unique_techs['unique_tech_message']
        weekly_tech_message = result_with_unique_techs['weekly_tech_message']

        self.assertIsInstance(unique_tech_message, str)
        self.assertIsInstance(weekly_tech_message, str)

        self.assertIn('List of unique techs learnt this week', unique_tech_message)
        self.assertIn('List of techs reported this week', weekly_tech_message)

        # Test case with no unique techs learned
        event_without_unique_techs = {
            "channel": "main"
        }

        result_without_unique_techs = lambda_handler(event_without_unique_techs, None)

        self.assertIsNotNone(result_without_unique_techs)
        self.assertIn('unique_tech_message', result_without_unique_techs)
        self.assertIn('weekly_tech_message', result_without_unique_techs)

        unique_tech_message_no_unique_techs = result_without_unique_techs['unique_tech_message']
        weekly_tech_message_no_unique_techs = result_without_unique_techs['weekly_tech_message']

        self.assertIsInstance(unique_tech_message_no_unique_techs, str)
        self.assertIsInstance(weekly_tech_message_no_unique_techs, str)

        self.assertIn('*No unique techs* learnt this week!! :(', unique_tech_message_no_unique_techs)
        self.assertIn('List of techs reported this week', weekly_tech_message_no_unique_techs)

