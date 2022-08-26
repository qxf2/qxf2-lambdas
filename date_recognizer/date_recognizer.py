"""
Extracts date from provided text"
"""

import sys
import datetime
import lexnlp.extract.en.dates as lexnlp

def extract_date(text):
    "Extracts the date from the provided text"
    date_list = list(lexnlp.get_dates(text))
    
    extracted_date=None
    if len(date_list) == 0:
        if "tomorrow" in text:
            extracted_date = datetime.date.today() + datetime.timedelta(days=1)
        elif "today" in text:
            extracted_date = datetime.date.today()
    else:
        extracted_date = date_list[0]
    return extracted_date

if __name__=="__main__":
    text=' '.join(sys.argv[1:])
    extracted_date = extract_date(text)
    print(extracted_date)
