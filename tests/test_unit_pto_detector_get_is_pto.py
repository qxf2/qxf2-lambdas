import requests
from parameterized import parameterized_class

@parameterized_class(("url", "message", "score", "expected_status_code"), [
   ("https://practice-testing-ai-ml.qxf2.com/is-pto","I am on PTO today", 1, 200),
   ("https://practice-testing-ai-ml.qxf2.com/is-pto","I am happy today", 0, 200),
])

class Testgetispto(object):
    """
    Test class for get is pto method
    """
    #@responses.activate
    def test_unit_get_is_pto_score(self):
        """
        Unit test for pto_score
        """
        resp = requests.post(self.url, data={"message":self.message})
        assert resp.status_code == self.expected_status_code
        assert resp.json()['score'] == self.score
