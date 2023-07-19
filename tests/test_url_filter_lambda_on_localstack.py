"""
Test URL Filter Lambda on the LocalStack:
- Deploy Lambda along with its dependencies and SQS
- Run test
- Delete Lambda and SQS queue
"""
import time
from unittest import TestCase
import tests.testutils as testutils

class UrlFilterLambdaLocalStackTest(TestCase):
    "Deploy Lambda, SQS on LocalStack and run the test"
    @classmethod
    def setup_class(cls):
        "Create SQS and Lambda"
        print('\nCreating a SQS')
        testutils.create_queue('test-queue')
        print('\nCreating the Lambda')
        testutils.create_lambda('url_filtering_lambda_rohini')
        cls.wait_for_function_active('url_filtering_lambda_rohini')

    @classmethod
    def teardown_class(cls):
        "Delete the Lambda, SQS  and teardown the session"
        print('\nDeleting the Lambda')
        testutils.delete_lambda('url_filtering_lambda_rohini')
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

    def test_that_lambda_returns_filtered_url(self):
        "Test Lambda's received message"
        print('\nInvoking the Lambda and verifying return message')
        message = {
                    "Records": [
                        {
                        "body": "{\"Message\":\"{\\\"msg\\\": \\\"Checkout how we can test Lambda "
                        "locally using LocalStack "
                        "https://qxf2.com/blog/testing-aws-lambda-locally-using-localstack-and-pytest\\\","
                        "\\\"chat_id\\\": \\\"dummy_chat@id.007\\\", "
                        "\\\"user_id\\\":\\\"dummy_user.id.007\\\"}\"}"
                        }
                    ]
                    }
        payload = testutils.invoke_function_and_get_message('url_filtering_lambda_rohini', message)
        self.assertEqual(payload['body'], '["https://qxf2.com/blog/testing-aws-lambda-locally-using-localstack-and-pytest"]')
