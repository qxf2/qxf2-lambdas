"""
Lambda to update neo4j database with respect to graphql data
"""
import json
import requests
import os
from urllib.parse import urljoin

API_KEY = os.environ.get('API_KEY')
URL = os.environ.get('URL')

def get_employees_graphql():
    "Get the employees from graphql"
    
    get_employee_url = urljoin(URL, 'survey/admin/employees')
    graphql_employees = requests.get(get_employee_url,headers={"User":API_KEY}).json()
    return graphql_employees

def get_employees_neo4j(employee_email):
    "Get employee details from neo4j via email"

    get_employee_by_email_url = urljoin(URL, 'survey/admin/get_employee_by_email')
    employee_details = requests.post(get_employee_by_email_url, data=employee_email, headers={"User":API_KEY}).json()
    return employee_details

def add_new_employee(employee):
    "Add new employee to database"
    
    add_employee_url = urljoin(URL, 'survey/admin/new_employee')
    emp_data = {"data":{"firstName":employee['firstName'],"lastName":employee['lastName'],"email":employee['email'],"fullName":employee['fullName'],"status":employee['status']}}
    emp_data = json.dumps(emp_data)
    add_employee = requests.post(add_employee_url, data=emp_data, headers={"User":API_KEY})
    return add_employee

def set_employee_status(employee_status_data):
    "Update status of employee"
    
    update_status_url = urljoin(URL, 'survey/admin/update_employee_status')
    update_status = requests.post(update_status_url, data=employee_status_data, headers={"User":API_KEY}).json()
    return update_status

def employee_add_status(add_employee,employee):
    if add_employee.status_code == 200:
        add_status = "Successfully added new employee %s"%employee
    else:
        add_status = "Failed to add new employee"
    return add_status

def lambda_handler(event, context):
    "Method run when Lambda is triggered"
      
    graphql_employees = get_employees_graphql()   
    add_status = "No new employees to add"
    update_status = ["The active status of all the employees are up to date"]
    for employee in graphql_employees:
        employee_email = {"email":employee['email']}
        employee_email = json.dumps(employee_email)
        employee_details = get_employees_neo4j(employee_email)

        if employee_details == "Employee does not exist" and employee['email'] != os.environ.get('EMAIL'):
            add_employee = add_new_employee(employee)
            add_status = employee_add_status(add_employee, employee['fullName'])

        if employee_details != "Employee does not exist":
            if employee_details[0]['employee_details']['status'] != employee['status']:
                employee_status_data = {"email":{"email":employee['email']},"status":{"employee_status":employee['status']}}
                employee_status_data = json.dumps(employee_status_data)
                update_employee_status = set_employee_status(employee_status_data)
                if update_status[0] == "The active status of all the employees are up to date":
                    update_status.pop(0)
                update_status.append(update_employee_status[0])
    return add_status, update_status
        