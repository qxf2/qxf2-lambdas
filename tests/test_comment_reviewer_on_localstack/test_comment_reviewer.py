#test_comment_reviewer_lambda.py

"""
Test Lambda on the LocalStack:
- Deploy Lambda along with its dependencies
- Run test
- Delete Lambda
"""
import time
from unittest import TestCase
import testutils

class CommentReviewerTest(TestCase):
    "Test to verify Lambda response"

    @classmethod
    def setup_class(cls):
        "Create SQS and lambda"
        print('\nCreating a SQS')
        testutils.create_queue('test-queue')
        print('\nCreating a comment_reviewer')
        testutils.create_lambda('comment_reviewer')
        cls.wait_for_function_active('comment_reviewer')

    @classmethod
    def teardown_class(cls):
        "Delete the Lambda, SQS  and teardown the session"
        print('\nDeleting the comment_reviewer')
        testutils.delete_lambda('comment_reviewer')
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

    def test_that_lambda_returns_comment_reviewer(self):
        "Trigger and test Lambda's received message"
        print('\nInvoking the Lambda and verifying return message')
        event = {
                "Records": [
                {
                    "body": "{\"Message\":\"{\\\"msg\\\": \\\"comment reviewers, please @qxf2bot!\\\", \\\"chat_id\\\": \\\"mailto:19:anythingh3r3@thread.skype\\\", \\\"user_id\\\":\\\"blah\\\"}\"}"
                }
                ]
            }

        # Invoke the Lambda function locally using LocalStack
        response = testutils.invoke_function_and_get_comment_reviewer('comment_reviewer', event)

        # Check if the response contains the expected message
        self.assertIn("Done!", response['body'])