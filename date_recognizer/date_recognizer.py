"""
Extracts date from provided text
"""

import sys
import datetime
from datefinder import find_dates
from enum import Enum


class Status(Enum):
    """
    Response status object
    """
    success = (200, 'Successfully obtained date from text')
    fail = (404, 'Unable to obtain date from text')
    error = (500, 'Internal error %s')


def extract_date(event: object,
                 context: object):
    """
    Extracts the date from the provided text
    :param event: data for lambda function to process
    :param context: methods & properties
    :param text: input str

    :return: response with status code, date, text
    """
    # Set defaults
    text = None
    response = {'statusCode': None,
                'headers': {'Content-Type': 'application/json'},
                'body': {'date': None, 'text':text}
                }

    # Set the initial state as Failed
    state = Status.fail
    extracted_date=None

    # Get the querystring passed with the URI
    text = event['queryStringParameters'].get('text')
    try:
        # Extract date from text
        date_list = list(find_dates(text))

        # If date not extracted, check if today/tomorrow present in text
        if len(date_list) == 0:
            if "tomorrow" in text:
                extracted_date = datetime.date.today() + datetime.timedelta(days=1)
            elif "today" in text:
                extracted_date = datetime.date.today()
        else:
            extracted_date = date_list[0]

        # Print debug message
        if extracted_date is not None:
            extracted_date = extracted_date.isoformat()
            state = Status.success
            print(state.value[1])
        else:
            print(state.value[1])

    except Exception as err:
        state = Status.error
        print(state.value[1] % err)

    finally:
        return {'statusCode': state.value[0],
                'headers': {'Content-Type': 'application/json'},
                'body': {'date': extracted_date,'text':text}
                }
