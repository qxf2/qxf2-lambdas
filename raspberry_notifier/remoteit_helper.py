"""
This script helps in fetching the devices registered with remote.it account
"""
import json
import sys
import time
import requests
from http_signature_helper import get_headers
from raspberry_helper import run_command_in_pi
from config import HOST


def list_devices():
    "Returns the list of online devices in remote.it"
    listing_url = "/apv/v27/device/list/all"
    headers = get_headers("GET", listing_url)
    try:
        response = requests.get("https://" + HOST + listing_url, headers=headers)
        list_data = json.loads(response.text)
        if list_data["status"] != "true":
            print("Unable to fetch list of devices: ", list_data["reason"])
            sys.exit(2)
        device_data = list_data["devices"]
        device_address_alias_map = {}
        ip_alias_map = {}
        for device in device_data:
            if device["servicetitle"] == "Bulk Service":
                ip_alias_map[device["devicelastip"].split(":")[0]] = device[
                    "devicealias"
                ]
        for device in device_data:
            if device["servicetitle"] == "SSH" and device["devicestate"] == "active":
                device_address = device["deviceaddress"]
                device_address_alias_map[device_address] = ip_alias_map[
                    device["devicelastip"].split(":")[0]
                ]
        if len(device_address_alias_map) == 0:
            print("No devices online")
            sys.exit(3)
    except Exception as error:
        print("Error while trying to get the list of devices", error)
        raise SystemExit(error)
    return device_address_alias_map


def connect_and_run(command, device_address, device_alias, conn):
    "Creates a proxy connection to the device, gets details of host and port and runs command"
    url_path = "/apv/v27/device/connect"
    payload = {"deviceaddress": device_address, "wait": "true", "hostip": "0.0.0.0"}
    body = json.dumps(payload)
    content_length = len(body)
    headers = get_headers("POST", url_path, content_length)
    try:
        time_now = time.time()
        response = requests.post(
            "https://" + HOST + url_path, headers=headers, data=body
        )
        print("Got response: {}", response.text)
        connect_data = json.loads(response.text)
        if connect_data["status"] == "true":
            proxy_server = connect_data["connection"]["proxyserver"]
            proxy_port = connect_data["connection"]["proxyport"]
            proxy_data = {
                "proxy_server": proxy_server,
                "proxy_port": proxy_port,
                "device_alias": device_alias,
            }
            print(
                "Time taken to get ip and port for "
                + device_alias
                + " is: "
                + str(time.time() - time_now)
            )
            run_command_in_pi(command, proxy_data, conn)
        else:
            print("Status of " + device_alias + " is false, device might be inactive")
    except Exception as error:
        print("Error while trying to connect to the device to get host/port", error)
