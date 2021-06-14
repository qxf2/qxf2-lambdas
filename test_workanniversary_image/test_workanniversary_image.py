"""
This module tests the generated work anniversary image. The text from image is extracted and predicted using Tesseract,
an (Optical Character Recognition) tool. It is compared against the data fetched from DB and verfies if the information
(employee name, anniversary and quote) is accurate.
"""
from os import name
import sys
import requests
import datetime
from datetime import date
import cv2
import pytesseract
import json
from difflib import SequenceMatcher
import numpy as np
from PIL import Image

BASE_URL = 'https://qxf2-employees.qxf2.com/graphql'

#TODO: Remove these once deployed in the lambda
#Put user credentials file in the lambda
USERNAME = "rohanJ"
PASSWORD = "1. b3 e5 2. Bb2 f6!"

#The methods authenticate and get_all_employees are picked from work_anniversary script
def authenticate():
    "Return an authenticate code"
    query = f"""mutation {{
        auth(password: "{PASSWORD}", username: "{USERNAME}") {{
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

def get_text_and_compare():
    file = 'work_anniversary_Drishya.png'
    extracted_text = extract_text(file)
    splitted_text = split_text(extracted_text)
    matched_emp_db_data = check_if_work_anniversary(splitted_text)

    anniversary_matched = False
    #Handle the case of the number '1' from the word '1st' not getting predicted properly
    special_words = ["1st","lst","Ist"]
    anniversary = None
    #Get the anniversary number fetched from db and check if any emp data is there
    if matched_emp_db_data != None:
        anniversary = matched_emp_db_data['anniversary']
    else:
        print("No employee matched")
        exit(1)
    
    anniv_from_image = splitted_text['anniversary']
        
    #check if anniversary number matches
    if anniversary == anniv_from_image or anniv_from_image in special_words:
        print("Anniversary matched: " + anniversary)
        anniversary_matched = True
    else:
        print("Anniversary didn't match: from DB: " + str(anniversary) + ", from Image: " + str(splitted_text['anniversary']))
    
    #check if quote matches
    quoteList = matched_emp_db_data['quotes']
    quote_matched = False
    for quote in quoteList:
        match_percent = SequenceMatcher(None, splitted_text['quote'], quote).ratio() * 100
        if match_percent > 90:
            print("Matched quote: " + quote + " percent matched: " + str(match_percent))
            quote_matched = True
            break
    if quote_matched and anniversary_matched:
        exit(0)
    else:
        print("No employee matched")
        exit(1) 

def extract_text(file):
    "Extract the text from the image"
    image = cv2.imread(file)

    template = cv2.imread('Work_anniversary_template.png')

    #Subtract the image from template to get just the text 
    img = image - template

    #TODO : Remove this, do not need an image
    cv2.imwrite("subtractedImage.png", img)

    #crop text portion in the image
    x = 350
    y = 500
    w = 2800
    h = 800
    img = image[y:y+h, x:x+w]

    #TODO: Remove this
    cv2.imwrite("cropped.jpg", img)
     
    # Apply OCR on the cropped image using the trained model 
    # TODO : Rename the model name
    text = pytesseract.image_to_string(img, lang='eng.casanova.copy')
    return text

def split_text(extracted_text):
    "Split the extracted text from image into into name, anniversary and quote"
    #For the Name and anniversary number
    firstline = ""
    #For the quote
    restOfTheLines = ""
    
    textList = extracted_text.split('\n')
    for line in textList:
        if line.strip() == "":
            continue
        if firstline == "":
            firstline = line.strip()
        else:
            restOfTheLines = restOfTheLines + " " + line.strip()
    restOfTheLines = restOfTheLines.strip()

    firstLineList = firstline.split(" ")

    #We need name which starts from 5th word
    if len(firstLineList) > 4:
        #The second word is the anniversary number
        nthAnniversary = firstLineList[1]
        name = ""
        #Extract the name
        i = 4
        while (len(firstLineList) > i):
            name = name + " " + firstLineList[i]
            i = i + 1
    
    splitted_data = {'name': name, 'anniversary': nthAnniversary, 'quote': restOfTheLines}
    print("Extracted data from image", splitted_data)
    return splitted_data

def get_anniversary_word(emp_joined_date):
    "Add suffix to the anniversary number fetched from database"
    today = datetime.datetime.today()
    day = today.day
    month = today.month
    year = today.year
    emp_joined_date_final = datetime.datetime.strptime(emp_joined_date,"%d-%b-%y")
    
    if day == emp_joined_date_final.day and month == emp_joined_date_final.month and emp_joined_date_final.year < year:
        suffix = "th"
        no_years = year - emp_joined_date_final.year
        if no_years == 1:
            suffix = "st"
        elif no_years == 2:
            suffix = "nd"
        elif no_years == 3:
            suffix = "rd"
        return str(no_years) + suffix

def check_if_work_anniversary(splitted_text):
    "Check if the current day is work anniversary for an employee using data from database"
    #Get employee data from database
    emp_data = get_all_employees()
    with open('anniversary_quotes.txt',encoding="utf8") as json_file:
        quote_data = json.load(json_file)
    
    matched_emp_db_data = None
    #Get the joining date from database
    for each_emp in emp_data:
        emp_joined_date = each_emp['node']['dateJoined']
        emp_joined_date = "14-Jun-20"

        #Get the employee name from database and compare against the extracted text from image
        if emp_joined_date is not None:
            emp_name = each_emp['node']['firstname'] + " " + each_emp['node']['lastname']
            #Return a measure of the similarity between data from database and  data from image
            match_percent = SequenceMatcher(None, splitted_text['name'], emp_name).ratio() * 100
            if match_percent < 80:
                continue
            #Get the anniversary number from database
            anniversary = get_anniversary_word(emp_joined_date)
            if anniversary == None:
                print("Anniversary is not today")
            else:
                matched_emp_db_data = {'name': emp_name, 'anniversary': anniversary, 'quotes': quote_data[emp_name]}
                break
    return matched_emp_db_data

if __name__ == "__main__":
    get_text_and_compare()
    


    