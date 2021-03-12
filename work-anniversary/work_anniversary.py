"""
Get employees joining date and post work anniversary image to skype 
"""

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
import textwrap
import time


SKYPE_URL = 'https://skype-sender.qxf2.com/send-image'
BASE_URL = 'https://qxf2-employees.qxf2.com/graphql'
inflect_obj = inflect.engine()


#clear this after updating
emp_data = [{'node': {'email': 'mak@qxf2.com', 'firstname': 'Sachin', 'lastname': 'T', 'dateJoined': '11-Mar-13', 'isActive': 'Y'}},{'node': {'email': 'mak@qxf2.com', 'firstname': 'Virender', 'lastname': 'S', 'dateJoined': '11-Mar-12', 'isActive': 'Y'}},
{'node': {'email': 'mak@qxf2.com', 'firstname': 'Rahul', 'lastname': 'D', 'dateJoined': '11-Mar-11', 'isActive': 'Y'}},
{'node': {'email': 'mak@qxf2.com', 'firstname': 'Sourav', 'lastname': 'G', 'dateJoined': '11-Mar-13', 'isActive': 'Y'}}]

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
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url = BASE_URL, json = {'query': query}, headers =\
        headers)
    all_employees = response.json().get('data', {}).get('allEmployees', {}).get('edges', [])
    return all_employees

def is_active_employee(each_node):
    "Check the employee is active or not"
    result_flag = True if each_node['node']['isActive'] == 'Y' else False
    return result_flag

def get_default_quotes(data,difference_in_years):
    quote_string = random.choice(data['experienced']) if difference_in_years != '1st' else random.choice(data['1st'])
    return quote_string

def calculate_work_anniversary(emp_joined_date, current_date, emp_name):
    "Calculate the difference"
    msg,quote_string = None,None
    if (emp_joined_date.month == current_date.month and emp_joined_date.day == current_date.day):
        difference_in_years = inflect_obj.ordinal(relativedelta(current_date, emp_joined_date).years)
        msg = f'Happy {difference_in_years} work anniversary {emp_name}'
        with open('anniversary_quotes.txt',encoding="utf8") as json_file:
            data = json.load(json_file)
        
        if emp_name in data.keys() :
            if len(data[emp_name]) >= 1:
                quote_string = random.choice(data[emp_name])
            else:
                quote_string = get_default_quotes(data,difference_in_years)
        else:
            quote_string = get_default_quotes(data,difference_in_years)    
        final_quote_string = '\n'.join(textwrap.wrap(quote_string, 70, break_long_words=False,subsequent_indent='\n'))
    return msg,final_quote_string

def add_text_to_image(message,emp_name,quote_string):
    image = Image.open('Work_anniversary_template.png')
    draw = ImageDraw.Draw(image)
    font1 = ImageFont.truetype('Casanova_Font_Free.ttf', size=130)
    font2 = ImageFont.truetype('Casanova_Font_Free.ttf', size=95)

    # starting position of the message
    (x, y) = (650, 500)
    color = 'rgb(128, 0, 128)' # purple color
    draw.text((x, y), message, fill=color, font=font1)

    (x, y) = (400, 700)
    color = 'rgb(255, 69, 0)' # orange color
    draw.text((x, y), quote_string, fill=color, font=font2)

    filepath = emp_name+ '_greeting_card.png'
    
    #filepath = '/tmp/' +emp_name+ '_greeting_card.png' #uncomment this later
    image.save(filepath,quality=95)
    return filepath

def send_image(img, img_name, channel_id = credentials.CHANNEL_ID):
    data = {'API_KEY' : credentials.API_KEY,
    'img_name' : img_name,
    'channel' : channel_id}
    files = [
        ('document', (img_name, open(img, 'rb'), 'application/octet')),
        ('data', ('data', json.dumps(data), 'application/json')),
        ]
    response = requests.post(SKYPE_URL, files = files)
    time.sleep(2)
    return response.status_code #uncomment this later

def is_qxf2_anniversary(current_date):
    "Check if its Qxf2's anniversary"
    if (current_date.month == 2 and current_date.day == 1):
        qxf2_start_date = datetime.datetime.strptime('01-Feb-13',"%d-%b-%y")
        difference_in_years = inflect_obj.ordinal(relativedelta(current_date, qxf2_start_date).years)
        msg = f'Qxf2 {difference_in_years} Year Anniversary'
        quote_string = 'Wishing a Great Success Ahead'
        file_path = add_text_to_image(msg, 'qxf2', quote_string)
        send_image(file_path,'work_anniversary')
    
def is_work_anniversary():
    "Get the work anniversary"
    #emp_data = get_all_employees()  #uncomment this later               
    for each_node in emp_data:
        print(each_node['node']['firstname'])
        employee_active = is_active_employee(each_node)
        emp_joined_date = each_node['node']['dateJoined']
        if employee_active and emp_joined_date is not None:
            emp_name = each_node['node']['firstname'] + " "+each_node['node']['lastname']
            emp_joined_date = datetime.datetime.strptime(emp_joined_date,"%d-%b-%y")
            current_date = date.today()
            message,quote_string = calculate_work_anniversary(emp_joined_date, current_date, emp_name)
            if message is not None:
                file_path = add_text_to_image(message,emp_name,quote_string)
                status_code = send_image(file_path,'work_anniversary') 
                os.remove(file_path)  #uncomment this later
    is_qxf2_anniversary(current_date)


def lambda_handler(event, context):
    "lambda entry point"
    is_work_anniversary()

if __name__ == "__main__":
    is_work_anniversary()

