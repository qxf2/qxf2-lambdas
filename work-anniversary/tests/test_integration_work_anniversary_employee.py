"""
Integration test between work anniversary lambda and employees service
"""

import os
import sys
import boto3
from unittest import mock
from unittest.mock import patch
from work_anniversary import work_anniversary
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@patch('work_anniversary.get_all_employees',return_value=[{'node':{'email':'test@qxf2.com','firstname':'Test','lastname':'Qxf2','dateJoined':'03-Feb-2013','isActive':'Y'}}])
@patch('work_anniversary.credentials.PASSWORD', 'new_value') 
def test_work_anniversary_employee_service(mock_get_all_employees):
    event = {}
    work_anniversary.lambda_handler(event=event, context=None)
    emp_data = mock_get_all_employees
    assert emp_data == [{'node':{'email':'test@qxf2.com','firstname':'Test','lastname':'Qxf2','dateJoined':'03-Feb-2013','isActive':'Y'}}]


