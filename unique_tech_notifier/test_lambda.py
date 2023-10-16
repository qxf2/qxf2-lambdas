import unittest
from unique_tech_notifier import lambda_handler

class TestLambda(unittest.TestCase):

    def test_lambda_handler(self):
        test_event = {
            'channel': 'main'
        }

        result = lambda_handler(test_event, None)

        self.assertIsNotNone(result)
        self.assertIn('unique_tech_message', result)
        self.assertIn('weekly_tech_message', result)


if __name__ == '__main__':
    unittest.main()

