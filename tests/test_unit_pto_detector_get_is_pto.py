import responses
import requests
import unittest
from parameterized import parameterized, parameterized_class

@parameterized_class(("message", "score", "expected_status_code"), [
   ("I am on PTO today", 1, 200),
])

class Testgetispto(unittest.TestCase):
    """
    Test class for get is pto method
    """
    @responses.activate
    def test_unit_get_is_pto_score(self):
        """
        Unit test for pto_score
        """
        responses.add(
            responses.POST,
            url='https://practice-testing-ai-ml.qxf2.com/is-pto',
            body='{"message":"I am on PTO today","score":1}',
            match=[
                responses.urlencoded_params_matcher({"message":self.message})
            ]
        )
        resp = requests.post("https://practice-testing-ai-ml.qxf2.com/is-pto", data={"message":self.message})
        self.assertEqual(resp.status_code,self.expected_status_code)
        self.assertEqual(resp.json()['score'],self.score)

if __name__ == "__main__":
    unittest.main()