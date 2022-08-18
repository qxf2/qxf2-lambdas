"""
Query the Employee GraphQL endpoint
"""
import os
import requests
BASE_URL = 'https://qxf2-employees.qxf2.com/graphql'

def authenticate():
    """
    Return an authenticate code
    Params:
        None
    Returns:
        accessToken : string
    """
    query = f"""mutation {{
        auth(password: "{os.environ['calendar_password']}", username: "{os.environ['calendar_username']}") {{
            accessToken
            refreshToken
            }}
        }}
    """
    response = requests.post(url = BASE_URL, json = {'query': query}, timeout = 30)
    return response.json().get('data',{}).get('auth',{}).get('accessToken',None)

def get_valid_emails():
    """
    Returns active employee email IDs
    Params:
        None
    Returns:
        employee_emails : list
    """
    employee_emails = []
    employees = query_all()
    for employee_node in employees:
        if employee_node['node']['isActive'] == 'Y':
            employee_emails.append(employee_node['node']['email'])
    return employee_emails

def query_all():
    """
    allEmployees query for the GraphQL service
    Params:
        None
    Returns:
        all_employees : list of dicts
    """
    query = """query
    findAllEmployees{
        allEmployees{
            edges{
                node{
                    email
                    employeeId
                    dateJoined
                    isActive
                    blogAuthorName
                }
            }
        }
    }"""
    access_token = authenticate()
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url = BASE_URL, json = {'query': query}, headers =
                                            headers, timeout = 30)
    all_employees = response.json().get('data', {}).get('allEmployees', {}).get('edges', [])
    return all_employees
