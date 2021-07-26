"""
Module to connect to raspberry pi using remoteit. All devices must be registered with 
a single remoteit account. The lambda will connect to all the devices which are online 
in the remoteit account and run a python file which  plays out voice on the pi.
"""

import json
import requests
import paramiko
import credentials as credentials

developerkey = credentials.developerkey

def login():
    "Logs in to the provided remoteit account"
    login_url = "https://api.remot3.it/apv/v27/user/login"
    payload = (
        '{"username": "'
        + credentials.username
        + '","password": "'
        + credentials.password
        + '"}'
    )
    headers = {"developerkey": developerkey, "Content-Type": "text/plain"}
    response = requests.request("POST", login_url, headers=headers, data=payload)
    login_data = json.loads(response.text)
    token = login_data["token"]
    return token

token = login()

def list_devices():
    "Returns the list of online devices in remoteit"
    listing_url = "https://api.remot3.it/apv/v27/device/list/all"
    payload = {}
    headers = {"developerkey": developerkey, "token": token}
    response = requests.request("GET", listing_url, headers=headers, data=payload)
    list_data = json.loads(response.text)
    device_data = list_data["devices"]
    address_list = []
    for device in device_data:
        if device["servicetitle"] == "SSH" and device["devicestate"] == "active":
            device_address = device["deviceaddress"]
            address_list.append(device_address)
    return address_list


def get_device_hostport_list():
    "Creates a proxy connection to the device, gets details of host and port"
    device_list = list_devices()
    server_list = []
    for device_address in device_list:
        connect_url = "https://api.remot3.it/apv/v27/device/connect"
        payload = (
            '{    "deviceaddress":"'
            + device_address
            + '",    "wait":"true",    "hostip":"0.0.0.0"}'
        )
        headers = {
            "developerkey": developerkey,
            "token": token,
            "Content-Type": "text/plain",
        }
        response = requests.request("POST", connect_url, headers=headers, data=payload)
        connect_data = json.loads(response.text)
        if connect_data["status"] == "true":
            proxy_server = connect_data["connection"]["proxyserver"]
            proxy_port = connect_data["connection"]["proxyport"]
            server_list.append({"proxy_server": proxy_server, "proxy_port": proxy_port})
    return server_list


def run_command_in_pi():
    "Connects to each device and runs a python file"
    proxy_data_list = get_device_hostport_list()
    i = 0
    file_to_copy = "call_out_to_colleagues.py"
    for proxy_data in proxy_data_list:
        proxy_port = proxy_data["proxy_port"]
        proxy_server = proxy_data["proxy_server"]
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(
                proxy_server,
                username=credentials.proxy_username,
                password=credentials.proxy_password,
                port=proxy_port,
                banner_timeout=200,
            )

            sftp = ssh.open_sftp()
            try:
                sftp.stat("/home/pi/" + file_to_copy)
                print("file exists")
            except Exception as exception:
                sftp.put(file_to_copy, "/home/pi/" + file_to_copy)
                print("Copied file")

            lines = []
            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(
                "python call_out_to_colleagues.py"
            )
            lines.append(ssh_stdout.readlines())
            lines.append(ssh_stderr.readlines())
            print("Output from device " + str(i) + " is: \n" + str(lines) + "\n")

        except Exception as exception:
            print(exception)
        i = i + 1


if __name__ == "__main__":
    # def run_command_in_pi(event, context):
    "lambda entry point"
    run_command_in_pi()
