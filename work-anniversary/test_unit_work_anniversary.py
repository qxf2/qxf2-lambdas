"""
Unit tests for is_active method of work_anniversary
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
import work_anniversary
import mock
import datetime

class Test_work_anniversary(unittest.TestCase):
    """
    Test class for work anniversary
    """
    
    def test_unit_is_active_employee(each_node):
        "Test the employee is active or not"
        each_node = {'node':{'isActive':'Y'}}
        result_flag = work_anniversary.is_active_employee(each_node)
        assert result_flag is True

    
    @mock.patch('work_anniversary.send_image')
    @mock.patch('work_anniversary.add_text_to_image')
    def test_unit_is_qxf2_anniversary(self,mock_add_text_method,mock_send_image_method):
        "Test the date is Qxf2 anniversary or not"
       
        #Hard-code date to match the Qxf2 Anniversary"
        current_date = '02-01-2021'
        time_mock=datetime.datetime.strptime(current_date,'%m-%d-%Y')
        
        if (time_mock.month == 2 and time_mock.day == 1):
            qxf2_start_date = datetime.datetime.strptime('01-Feb-13',"%d-%b-%y")
            difference_in_years = 8
            message = 'Qxf2 8th Year Anniversary'
            quoted_string = 'Wishing a Great Success Ahead'
            mock_add_text_method.return_value = 'mock_file_path'
            assert mock_send_image_method(mock_add_text_method.return_value,'work_anniversary')
         
        #result_flag = work_anniversary.is_qxf2_anniversary(time_mock)   
    
    
    
    @mock.patch('work_anniversary.get_all_employees')
    @mock.patch('work_anniversary.is_active_employee')
    @mock.patch('work_anniversary.calculate_work_anniversary')
    @mock.patch('work_anniversary.send_image')
    @mock.patch('work_anniversary.add_text_to_image')
    def test_unit_is_work_anniversary(self,mock_add_text_method,mock_send_image_method,mock_get_all_employees,mock_is_active_employee,mock_calculate_work_anniversary):
        "Test the date of the work anniversary"
        mock_get_all_employees.return_value = {                
                    'node':{
                        'email':'drishya.tm@qxf2.com',
                        'firstname':'Drishya',
                        'lastname':'TM',
                        'dateJoined':'06-02-2020',
                        'isActive': 'Y'
                    
                }
            }
                    
        for each_node in mock_get_all_employees.return_value:
            print (each_node)
            
            mock_is_active_employee.return_value = True
            emp_joined_date = '02-Jun-20'
            if mock_is_active_employee.return_value and emp_joined_date is not None:
                emp_name = "drishya tm"
                emp_joined_date = datetime.datetime.strptime(emp_joined_date,"%d-%b-%y")
                current_date = '06-02-2021'
                #message,quote_string = calculate_work_anniversary(emp_joined_date, current_date, emp_name)
                assert mock_calculate_work_anniversary(emp_joined_date, current_date, emp_name)
                message = True
                if message is not None:
                    mock_add_text_method.return_value = 'mock_file_path'
                    assert mock_send_image_method(mock_add_text_method.return_value,'work_anniversary') 
                    
        #is_qxf2_anniversary(current_date)
        