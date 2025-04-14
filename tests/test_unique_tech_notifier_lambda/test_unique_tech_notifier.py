# test_unique_tech_notifier_lambda.py

import time
from unittest import TestCase
import testutils

class UniqueTechNotifierTest(TestCase):
    @classmethod
    def setUpClass(cls):
        # Create an SQS queue and deploy the Lambda
        print('\nCreating an SQS queue')
        testutils.create_queue('test-queue')
        print('\nCreating the unique_tech_notifier Lambda')
        testutils.create_lambda('unique_tech_notifier')
        cls.wait_for_function_active('unique_tech_notifier')

    @classmethod
    def tearDownClass(cls):
        # Delete the Lambda and the SQS queue
        print('\nDeleting the unique_tech_notifier Lambda')
        testutils.delete_lambda('unique_tech_notifier')
        print('\nDeleting the SQS test queue')
        queue_url = testutils.get_queue_url('test-queue')
        testutils.delete_queue(queue_url)

    @classmethod
    def wait_for_function_active(cls, function_name):
        # Wait until the Lambda function is active
        lambda_client = testutils.get_lambda_client()
        while True:
            response = lambda_client.get_function(FunctionName=function_name)
            function_state = response['Configuration']['State']
            if function_state == 'Active':
                break
            time.sleep(1)

    def test_lambda_returns_unique_tech(self):
        # Invoke the Lambda and verify the return message
        print('\nInvoking the Lambda and verifying the return message')
        event = {
            "key": "value"
        }

        # Invoke the Lambda function locally using LocalStack
        response = testutils.invoke_function_and_get_unique_tech('unique_tech_notifier', event)

        expected_substring = "*No unique techs* learnt this week!! :("

        self.assertIn(expected_substring, response['unique_tech'])
