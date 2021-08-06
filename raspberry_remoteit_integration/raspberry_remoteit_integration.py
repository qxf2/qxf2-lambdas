"""
Module to connect to raspberry pi using remoteit. All devices must be registered with 
a single remoteit account. The lambda will connect to all the devices which are online 
in the remoteit account and run a python file which  plays out voice on the pi.
"""

import json
import time
import traceback
from multiprocessing import Pipe, Process
import requests
import paramiko
import credentials as credentials


developer_key = credentials.developerkey


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
    headers = {"developerkey": developer_key, "Content-Type": "text/plain"}
    response = requests.request("POST", login_url, headers=headers, data=payload)
    login_data = json.loads(response.text)
    token = login_data["token"]
    return token


def list_devices(token):
    "Returns the list of online devices in remoteit"
    listing_url = "https://api.remot3.it/apv/v27/device/list/all"
    payload = {}
    headers = {"developerkey": developer_key, "token": token}
    response = requests.request("GET", listing_url, headers=headers, data=payload)
    list_data = json.loads(response.text)
    device_data = list_data["devices"]
    device_address_alias_map = {}
    ip_alias_map = {}
    for device in device_data:
        if device["servicetitle"] == "Bulk Service":
            ip_alias_map[device["devicelastip"]] = device["devicealias"]
    for device in device_data:
        if device["servicetitle"] == "SSH" and device["devicestate"] == "active":
            device_address = device["deviceaddress"]
            device_address_alias_map[device_address] = ip_alias_map[
                device["devicelastip"]
            ]
    return device_address_alias_map


def connect_and_run(token, command, device_address, device_alias, conn):
    "Creates a proxy connection to the device, gets details of host and port and run command"
    time_now = time.time()

    # print("Trying to fetch proxy host and port for " + device_list[device_address])
    connect_url = "https://api.remot3.it/apv/v27/device/connect"
    payload = (
        '{    "deviceaddress":"'
        + device_address
        + '",    "wait":"true",    "hostip":"0.0.0.0"}'
    )
    headers = {
        "developerkey": developer_key,
        "token": token,
        "Content-Type": "text/plain",
    }
    response = requests.request("POST", connect_url, headers=headers, data=payload)
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


def run_command_in_pi(command, proxy_data, conn):
    "Connects to each device and executes a command"

    time_now = time.time()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    proxy_port = proxy_data["proxy_port"]
    proxy_server = proxy_data["proxy_server"]
    device_alias = proxy_data["device_alias"]
    try:
        print("Trying to ssh to " + device_alias)
        ssh.connect(
            proxy_server,
            username=credentials.proxy_username,
            password=credentials.proxy_password,
            port=proxy_port,
            banner_timeout=20,
        )
        # run_sftp(ssh, "test.sh")
        ssh_command = (
            "espeak -ven-us+f3 -s 125 --stdout '" + command + "' | aplay 2>/dev/null"
        )
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(ssh_command)
        print(
            "\nTime taken to ssh and run espeak for : "
            + device_alias
            + " : "
            + str(time.time() - time_now)
        )
        print("\nStdout from " + device_alias + ": " + str(ssh_stdout.readlines()))
        print("\nStderr from " + device_alias + ": " + str(ssh_stderr.readlines()))

    except Exception as exception:
        print(
            "\nError while running espeak for "
            + device_alias
            + ", time taken: "
            + str(time.time() - time_now)
        )
        print(exception)
        print(traceback.format_exc())
        conn.close()


def run_sftp(ssh, file_to_copy):
    "Copy files to the device"
    sftp = ssh.open_sftp()
    try:
        sftp.stat("/home/pi/" + file_to_copy)
        print("file exists")
    except:
        sftp.put(file_to_copy, "/home/pi/" + file_to_copy)
        print("Copied file")


def run_in_parallel(command):
    "Runs multiple processes"
    parent_connections = []
    processes = []
    token = login()
    device_address_alias_dict = list_devices(token)
    for device_address in device_address_alias_dict:
        device_alias = device_address_alias_dict[device_address]

        parent_conn, child_conn = Pipe()
        parent_connections.append(parent_conn)
        # create the process, pass instance and connection
        process = Process(
            target=connect_and_run,
            args=(token, command, device_address, device_alias, child_conn),
        )
        processes.append(process)
    for process in processes:
        process.start()
    # make sure that all processes have finished
    for process in processes:
        process.join()

def trigger_notifications(event, context):
    "lambda entry point"
    command = event['msg']
    run_in_parallel(command)
