"""
Unit test for the work anniversary lambda. Tests the following rules:
* The name of employee is correct
* The year of the anniversary is correct
* The quote contents are from a given source
* The quote does not repeat for same user
Employee data and their respective quotes are mocked
"""
import os
import csv
from unittest.mock import Mock, patch
from datetime import date
import json
import datetime
from difflib import SequenceMatcher
import pytest
import mocked_employee_data
import image_data
import work_anniversary as work_anniv

def get_data():
    "Fetches test data from a CSV file"
    ret_list = []
    csv_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data.csv")
    with open(csv_file) as csvfile:
        boardreader = csv.reader(csvfile, delimiter="$")
        for row in boardreader:
            ret_list.append(row)
    return ret_list


@pytest.mark.parametrize("mocked_date_str, expected_json_str", get_data())
@patch("os.remove", Mock())
@patch("json.load")
@patch("work_anniversary.date")
@patch("work_anniversary.send_image")
@patch("work_anniversary.get_all_employees")
def test_call_work_anniv_lambda(
    mocked_emp_data,
    mocked_image,
    mocked_date,
    mocked_json,
    mocked_date_str,
    expected_json_str,
):
    "Prepares data and calls work anniversary lambda to genearate a mocked image"
    expected_json = json.loads(expected_json_str)
    mocked_employee_list = mocked_employee_data.mock_employee_data()
    mocked_emp_data.return_value = mocked_employee_list
    with open("mocked_quotes.txt", encoding="utf8") as json_file:
        mocked_quotes = json.loads(json_file.read())
    mocked_json.return_value = mocked_quotes
    mocked_date_obj = datetime.datetime.strptime(mocked_date_str.strip(), "%d-%b-%Y")
    mocked_date.today.return_value = mocked_date_obj
    work_anniv.lambda_handler(None, None)
    mocked_send_image_args_list = mocked_image.call_args_list

    assert_values(mocked_send_image_args_list, expected_json)


def assert_values(created_files, expected_list):
    "Compares the values fetched from image against employee data"

    assert len(created_files) == len(expected_list), \
        "Expected " + str(len(expected_list)) + " number of anniversary images, got " + str(len(created_files))
    for i in range(len(created_files)):
        created_file = created_files[i]
        file_name = created_file[0][0]
        extracted_img_data = image_data.get_data_from_image(file_name)
        assert extracted_img_data is not None
        print("The data extracted from image is ", extracted_img_data)
        match_percent_name = (
            SequenceMatcher(
                None, extracted_img_data["name"], expected_list[i]["name"]).ratio()* 100
        )
        assert match_percent_name > 80
        match_percent_quote = (
            SequenceMatcher(
                None, extracted_img_data["quote"], expected_list[i]["quote"]).ratio()* 100
        )
        assert match_percent_quote > 95
        assert extracted_img_data["anniversary"] == expected_list[i]["anniversary"]


@patch("os.remove", Mock())
@patch("json.load")
@patch("work_anniversary.date")
@patch("work_anniversary.send_image")
@patch("work_anniversary.get_all_employees")
def test_check_quote_repeat(
    mocked_emp_data, mocked_image, mocked_date_method, mocked_json):
    "checks if quote is repeated for an employee"
    mocked_quotes = {
        "experienced": [
            "Employees like you are the pride and joy of this company."
        ],
        "Rajeswari Gali": [
            "Happy work anniversary, employee #1!",
            "We look forward to your inspiring contributions",
            "Thank you for your dedication and support",
            "Wish you many happy work years at Qxf2",
        ],
    }
    used_quotes = []
    mocked_employee_list = mocked_employee_data.mock_employee_data()
    mocked_emp_data.return_value = mocked_employee_list
    mocked_dates = [
        date(2015, 12, 21),
        date(2016, 12, 21),
        date(2017, 12, 21),
        date(2018, 12, 21),
        date(2019, 12, 21),
    ]
    mocked_json.return_value = mocked_quotes

    for i in range(len(mocked_dates)):
        mocked_date = mocked_dates[i]
        quote_matched = False
        mocked_date_method.today.return_value = mocked_date
        work_anniv.lambda_handler(None, None)
        mocked_send_image_args_list = mocked_image.call_args_list
        assert len(mocked_send_image_args_list) == 1
        file_name = mocked_send_image_args_list[0][0][0]
        extracted_img_data = image_data.get_data_from_image(file_name)
        print("The extracted data of this employee is ", extracted_img_data)

        assert extracted_img_data is not None
        expected_employee_name = "Rajeswari Gali"

        match_percent_name = (
            SequenceMatcher(
                None, extracted_img_data["name"], expected_employee_name).ratio()* 100
        )
        assert match_percent_name > 80
        if i < 5:
            for quote in mocked_quotes[expected_employee_name]:
                match_percent_quote = (
                    SequenceMatcher(None, extracted_img_data["quote"], quote).ratio()* 100
                )
                if match_percent_quote > 95:
                    assert quote not in used_quotes, "Quote got repeated"
                    quote_matched = True
                    used_quotes.append(quote)
                    break
            assert quote_matched is True, "Quote did not match"
        else:
            for quote in mocked_quotes["experienced"]:
                match_percent_quote = (
                    SequenceMatcher(None, extracted_img_data["quote"], quote).ratio()
                    * 100
                )
                if match_percent_quote > 95:
                    quote_matched = True
                    break
            assert quote_matched is True, "Quote did not match from default"
        mocked_image.reset_mock()
