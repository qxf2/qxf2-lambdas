"Contract test for work anniversary"

import os
import json
import atexit
import unittest
import pytest
import requests
import logging
from pact import Consumer, Provider, Format

# Declaring logger
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
print(Format().__dict__)

#Declaring PACT directory
REPO_DIR = os.path.dirname(os.path.dirname(__file__))
PACT_DIR = os.path.join(REPO_DIR,'tests')


# Setting up pact
pact = Consumer('Consumer').has_pact_with(Provider('Provider'))
pact.start_service()
atexit.register(pact.stop_service)

print(pact)
class Workanniversary(unittest.TestCase):
    "Contract test"
    def test_check_employee_data_return(self):
        "check it's returning the correct employee data"
        expected = {
        'msg' : '{"errors":[{"message":"Must provide query string."}]}'
        }
        (pact\
        . given('Request to get home page') \
        . upon_receiving('a request for home page')\
        . with_request('GET', '/qxf2-employees.qxf2.com/graphql')\
        . will_respond_with(200, body=expected))\

        with pact:\
            result = requests.get(pact.uri + '/qxf2-employees.qxf2.com/graphql')\

        self.assertEqual(result.json(), expected)
        pact.verify()

