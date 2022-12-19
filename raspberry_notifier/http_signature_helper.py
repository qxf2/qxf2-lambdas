"""
This module provides the headers that are necessary to login to remote.it
"""
import datetime
from base64 import b64decode
import httpsig
import config
from config import HOST

DEVELOPER_KEY = config.DEVELOPER_KEY
ACCESS_KEY_ID = config.ACCESS_KEY_ID
SECRET_ACCESS_KEY = config.SECRET_ACCESS_KEY

CONTENT_TYPE = "application/json"


def get_token(request_method, path, headers):
    "Fetch token using Signature authentication"
    header_signer = httpsig.HeaderSigner(
        ACCESS_KEY_ID,
        b64decode(SECRET_ACCESS_KEY),
        algorithm="hmac-sha256",
        headers=[
            "(request-target)",
            "host",
            "date",
            "content-type",
            "content-length",
        ],
    )
    return header_signer.sign(headers, method=request_method, path=path)[
        "authorization"
    ]


def get_headers(request_method, path, content_length=0):
    "Set headers for the request including authentication token"
    date = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S%z")

    headers = {
        "host": HOST,
        "date": date,
        "content-type": CONTENT_TYPE,
        "DeveloperKey": DEVELOPER_KEY,
        "content-length": str(content_length),
    }
    headers["Authorization"] = get_token(request_method, path, headers)
    return headers
