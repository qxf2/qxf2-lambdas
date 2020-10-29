import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
import json
import os
import requests
import user_credentials as credentials
import inflect
from PIL import Image, ImageDraw, ImageFont
import random,time


SKYPE_URL = 'https://skype-sender.qxf2.com/send-image'
BASE_URL = 'https://qxf2-employees.qxf2.com/graphql'
inflect_obj = inflect.engine()

emp_data = [{'node': {'email': 'abc@qxf2.com', 'firstname': 'Rohan', 'lastname': 'Joshi', 'dateJoined': '28-Jan-20', 'isActive': 'Y'}},
{'node': {'email': 'xyz@qxf2.com', 'firstname': 'Rohan', 'lastname': 'Dudam', 'dateJoined': '29-Jan-19', 'isActive': 'Y'}},
{'node': {'email': 'pqr@qxf2.com', 'firstname': 'Shivahari', 'lastname': 'Pitchaikkannu', 'dateJoined': '29-Jan-14', 'isActive': 'Y'}},
{'node': {'email': 'def@qxf2.com', 'firstname': 'Avinash', 'lastname': 'Shetty', 'dateJoined': '29-Jan-15', 'isActive': 'Y'}},
 {'node': {'email': 'rst@qxf2.com', 'firstname': 'rs', 'lastname': 't', 'dateJoined': '29-Jan-16', 'isActive': 'N'}}]


emp_list = []
def authenticate():
    "Return an authenticate code"
    query = f"""mutation {{
        auth(password: "{credentials.PASSWORD}", username: "{credentials.USERNAME}") {{
            accessToken
            refreshToken
            }}
        }}
    """
    response = requests.post(url = BASE_URL, json = {'query': query})

    return response.json().get('data',{}).get('auth',{}).get('accessToken',None)

def get_all_employees():
    "Query allEmployees"
    query = """query
    findAllEmployees{
        allEmployees{
            edges{
                node{
                    email
                    firstname
                    lastname
                    dateJoined
                    isActive
                }
            }
        }
    }"""
    access_token = authenticate()
    print(f'Access token: {access_token}')
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url = BASE_URL, json = {'query': query}, headers =\
        headers)
    all_employees = response.json().get('data', {}).get('allEmployees', {}).get('edges', [])
    return all_employees

def is_active_employee(each_node):
    "Check the employee is active or not"
    result_flag = True if each_node['node']['isActive'] == 'Y' else False
    return result_flag


def calculate_work_anniversary(emp_joined_date, current_date, emp_name):
    "Calculate the difference"
    msg,quote_string = None,None
    if (emp_joined_date.month == current_date.month and emp_joined_date.day == current_date.day):
        difference_in_years = inflect_obj.ordinal(relativedelta(current_date, emp_joined_date).years)
        msg = f'Happy {difference_in_years} work anniversary {emp_name}'
        with open('anniversary_quotes.txt') as json_file:
            data = json.load(json_file)
        quote_string = random.choice(data['experienced']) if difference_in_years != '1st' else random.choice(data['1st'])
    return msg,quote_string

def add_text_to_image(message,emp_name,quote_string):
    image = Image.open('Work_anniversary_template.png')
    draw = ImageDraw.Draw(image)
    font1 = ImageFont.truetype('Casanova_Font_Free.ttf', size=120)
    font2 = ImageFont.truetype('Casanova_Font_Free.ttf', size=70)

    # starting position of the message
    (x, y) = (650, 700)
    color = 'rgb(128, 0, 128)' # purple color
    draw.text((x, y), message, fill=color, font=font1)

    (x, y) = (600, 900)
    color = 'rgb(255, 69, 0)' # orange color
    draw.text((x, y), quote_string, fill=color, font=font2)
    
    filepath = '/tmp/' +emp_name+ '_greeting_card.png'
    image.save(filepath,quality=95)
    send_image(filepath,'work_anniversary')
    os.remove(filepath)

def send_image(img, img_name, channel_id = credentials.CHANNEL_ID):
    data = {'API_KEY' : credentials.API_KEY,
    'img_name' : img_name,
    'channel' : channel_id}
    files = [
        ('document', (img_name, open(img, 'rb'), 'application/octet')),
        ('data', ('data', json.dumps(data), 'application/json')),
        ]
    response = requests.post(SKYPE_URL, files = files)

def is_work_anniversary():
    "Get the work anniversary"
    #emp_data = get_all_employees()
    for each_node in emp_data:
        employee_active = is_active_employee(each_node)
        emp_joined_date = each_node['node']['dateJoined']
        if employee_active and emp_joined_date is not None:
            emp_name = each_node['node']['firstname'] + " "+each_node['node']['lastname']
            emp_list.append(each_node)
            emp_joined_date = datetime.datetime.strptime(emp_joined_date,"%d-%b-%y")
            current_date = date.today()
            message,quote_string = calculate_work_anniversary(emp_joined_date, current_date, emp_name)
            
            if message is not None:
                add_text_to_image(message,emp_name,quote_string)

def lambda_handler(event, context):
    "lambda entry point"
    is_work_anniversary()



