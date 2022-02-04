"""
Lambda to update neo4j database with respect to graphql data
"""
import json
import requests
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

def lambda_handler(event, context):
    "Method run when Lambda is triggered"
      
    graphql_employees = get_employees_graphql()
       
    for employee in graphql_employees:
        employee_email = {"email":employee['email']}
        employee_email = json.dumps(employee_email)
        employee_details = get_employees_neo4j(employee_email)
        if employee_details == "Employee does not exist" and employee['email'] != "test@qxf2.com":
            add_employee = add_new_employee(employee)
            if add_employee.status_code == 200:
                print("Successfully added new employee",employee['fullName'])
            else:
                print("Failed to add new employee")
        
    
            
    
    
