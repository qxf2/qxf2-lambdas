"""
Test Lambda function using local testing tools (e.g., LocalStack):
- Deploy Lambda function along with its dependencies
- Run test cases to verify Lambda's functionality
- Delete Lambda function and related resources
"""
import time
import unittest
import testutils as testutils
from unique_tech_notifier import lambda_handler

class MyLambdaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Deploy the Lambda function and related resources here (e.g., SQS)
        print('\nCreating an SQS queue')
        testutils.create_queue('test-queue')
        print('\nCreating the Lambda function')
        testutils.create_lambda('my_lambda_function')
        cls.wait_for_function_active('my_lambda_function')

    @classmethod
    def tearDownClass(cls):
        # Delete the Lambda function and related resources here
        print('\nDeleting the Lambda function')
        testutils.delete_lambda('my_lambda_function')
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

            time.sleep(1)  # Wait for 1 second before checking again

    def test_lambda_with_unique_techs(self):
        # Test case with unique techs learned
        event_with_unique_techs = {
            "channel": "main"
        }

        result = lambda_handler(event_with_unique_techs, None)

        self.assertIsNotNone(result)
        self.assertIn('unique_tech_message', result)
        self.assertIn('weekly_tech_message', result)

        unique_tech_message = result['unique_tech_message']
        weekly_tech_message = result['weekly_tech_message']

        self.assertIsInstance(unique_tech_message, str)
        self.assertIsInstance(weekly_tech_message, str)

if __name__ == '__main__':
    unittest.main()
