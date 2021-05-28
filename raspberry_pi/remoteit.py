import requests
import json
#import paramiko
import time
import credentials as credentials


developerkey = credentials.developerkey

def login():
  print("THis is the login method")
  login_url = "https://api.remot3.it/apv/v27/user/login"
  payload = "{\"username\": \"" + credentials.username + "\",\"password\": \"" + credentials.password + "\"}"
  #print(payload)
  headers = {
    'developerkey': developerkey,
    'Content-Type': 'text/plain'
  }
  response = requests.request("POST", login_url, headers=headers, data=payload)
  #print(response.text)
  login_data = json.loads(response.text)
  token = login_data['token']
  print("the token is", token)
  #return token
  

token = login()

def list_devices():
  
  listing_url = "https://api.remot3.it/apv/v27/device/list/all"
  payload={}
  headers = {
    'developerkey': developerkey,
    'token': token
  }
  response = requests.request("GET", listing_url, headers=headers, data=payload)
  list_data = json.loads(response.text)
  device_data = list_data['devices']
  address_list = []
  for device in device_data:
    if device['servicetitle'] == 'SSH':
      device_address = device['deviceaddress']
      address_list.append(device_address)
  #print("Device address is", device_address)
  return address_list

def get_device_hostport_list():
  device_list = list_devices()
  server_list = []
  for device_address in device_list:
    connect_url = "https://api.remot3.it/apv/v27/device/connect"
    payload="{    \"deviceaddress\":\"" + device_address + "\",    \"wait\":\"true\",    \"hostip\":\"0.0.0.0\"}"
    headers = {
      'developerkey': developerkey,
      'token': token,
      'Content-Type': 'text/plain'
    }
    response = requests.request("POST", connect_url, headers=headers, data=payload)
    #print(response.text)
    connect_data = json.loads(response.text)
    if connect_data['status'] == 'true':
      proxy_server = connect_data['connection']['proxyserver']
      proxy_port = connect_data['connection']['proxyport']
      #print("The proxy server, port and device_address are ", proxy_server, proxy_port, device_address)
      server_list.append({'proxy_server':proxy_server, 'proxy_port':proxy_port})
  return server_list

"""
def run_command():
  proxy_data_list = get_device_hostport_list()
  i = 0
  file_to_copy='switch_on_led.py'
  for proxy_data in proxy_data_list:
    proxy_port = proxy_data['proxy_port']
    proxy_server = proxy_data['proxy_server']
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
      ssh.connect(proxy_server,username=credentials.proxy_username,
        password=credentials.proxy_password,port=proxy_port,banner_timeout=200)

      sftp = ssh.open_sftp()
      try:
        sftp.stat('/home/pi/' + file_to_copy)
        print('file exists')
      except:
        sftp.put(file_to_copy, '/home/pi/' + file_to_copy)
        print('Copied file')

      ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("ls -l")
      lines = ssh_stdout.readlines()
      ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("python callout_colleague.py")
      lines.append(ssh_stdout.readlines())
      print("Output from device " + str(i) + " is: \n" + str(lines) + "\n")
 
    except Exception as e:
      print(e)
    i = i + 1
"""
def run_command_in_pi(event, context):
    "lambda entry point"
    #return run_command()
    login()