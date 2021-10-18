"""
Contract test for daily PTO
"""
import atexit
import unittest
import requests
import json
from pact import Consumer, Provider,Like
from pact.matchers import get_generated_values

pact = Consumer('pto-detector-lambda').has_pact_with(Provider('pto-detector-instance'), host_name='localhost', port=1234)
pact.start_service()
atexit.register(pact.stop_service)

 """ pact test to build the contract between lambda provider and is_pto instance consumer """
class ContractTest(unittest.TestCase):
  def test_is_pto(self):
    expected = {"message":"I am doing fine today", "score": 0}
    payload = {"message":"I am doing fine today"}

    (pact
     .given('a correct pto message')
     .upon_receiving('to check if its a pto')
     .with_request('post', '/is-pto',body=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
     .will_respond_with(200,headers={'Content-Type':'application/json'}, body=expected))

    with pact:
      result = requests.post('http://localhost:1234/is-pto',data=payload,headers={'Content-Type': 'application/x-www-form-urlencoded'})
    self.assertEqual(result.json(), get_generated_values(expected))

if __name__ == "__main__":
     unittest.main()