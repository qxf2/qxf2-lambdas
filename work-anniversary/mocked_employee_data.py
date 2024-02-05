"""
Mock graphql employee data
"""

def mock_employee_data():
    "Mocks the employee data"
    all_employees = [
        {
            "node": {
                "email": "raji@qxf2.com",
                "firstname": "Rajeswari",
                "lastname": "Gali",
                "dateJoined": "21-Dec-14",
                "isActive": "Y",
            }
        },
        {
            "node": {
                "email": "rohini.gopal@qxf2.com",
                "firstname": "Rohini",
                "lastname": "Gopal",
                "dateJoined": "17-Aug-18",
                "isActive": "Y",
            }
        },
        {
            "node": {
                "email": "sravanti.tatiraju@qxf2.com",
                "firstname": "Sravanti",
                "lastname": "Tatiraju",
                "dateJoined": "17-Aug-17",
                "isActive": "Y",
            }
        },
        {
            "node": {
                "email": "drishya.tm@qxf2.com",
                "firstname": "Drishya",
                "lastname": "TM",
                "dateJoined": "13-Apr-18",
                "isActive": "Y",
            }
        },
        {
            "node": {
                "email": "preedhi.vivek@qxf2.com",
                "firstname": "Preedhi",
                "lastname": "Vivek",
                "dateJoined": "25-Feb-20",
                "isActive": "Y",
            }
        },
        {
            "node": {
                "email": "rohan.j@qxf2.com",
                "firstname": "Rohan",
                "lastname": "Joshi",
                "dateJoined": "01-Jan-20",
                "isActive": "Y",
            }
        },
    ]
    return all_employees
