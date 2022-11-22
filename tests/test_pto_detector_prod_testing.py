import boto3
from datetime import date
import logging
from logging.handlers import RotatingFileHandler
import json
import requests
import time
from botocore.exceptions import ClientError


AWS_Access_Key_ID = ""
AWS_Secret_Access_Key = ""
region = 'ap-south-1'
QUEUE_URL = 'https://sqs.ap-south-1.amazonaws.com/285993504765/skype-sender'

DELAY_TIME=10 # 10 Seconds
channel =''
instances = {
 'pto_app': [{ 'webid': 'https://practice-testing-ai-ml.qxf2.com/is-pto','instance_id' : "i-02f4637402d33fc07"}],'some_app': [{ 'webid': 'https://practice-testing-ai-ml.qxf2.com/is-pto','instance_id' : "123456"}]
}


ec2 = None

try:
  ec2 = boto3.client('ec2', aws_access_key_id=AWS_Access_Key_ID, aws_secret_access_key=AWS_Secret_Access_Key, region_name=region)
  sqs_client = boto3.client('sqs', aws_access_key_id=AWS_Access_Key_ID, aws_secret_access_key=AWS_Secret_Access_Key, region_name=region)
  # ec2 = boto3.resource('ec2',aws_access_key_id=AWS_Access_Key_ID, aws_secret_access_key=AWS_Secret_Access_Key, region_name=region)
except Exception as e:
  print(e)
  print("AWS CREDS ERROR, Exiting...")
  exit()

def give_alert(alert_message):
  "call function to give alert on skype message"
    
  message = str({'msg':f'{alert_message}', 'channel':channel})
  sqs_client.send_message(QueueUrl=QUEUE_URL, MessageBody=(message))

def monitorInstances(instancesIds):
  "call function to monitor the ec2 instance"
  
  if(type(instancesIds) != list):  
    instancesIds = [instancesIds]
  
  
  try:
    response_monitor = ec2.monitor_instances(InstanceIds=instancesIds, DryRun=False)
    response = ec2.describe_instances(InstanceIds=instancesIds)    
    status_instance= response['Reservations'][0]['Instances'][0]['State']['Name']
    if (status_instance == "running"):      
        pass_message = "Pass: Instance is up and Running and  Monitored"
        #give_alert(pass_message)
    else:
      failed_message = "PTO Detector Instance is Down. Kindly check it"
      print(response_monitor)
      print(response)
      print("")
      give_alert(failed_message)
    
  except ClientError as e:
    print(e)
    failed_message ="Failed : PTO Detector InstanceID is not a valid to Monitor"
    print(failed_message)
    give_alert(failed_message)
    


def startInstances(instancesIds):
  "call function to start the ec2 instance"
  if(type(instancesIds) != list):  
    instancesIds = [instancesIds]

  try:
    response = ec2.start_instances(InstanceIds=instancesIds, DryRun=False)
    print("Instances Started")
  except ClientError as e:
    print(e)
    print(response)
    failed_message = "Alert:PTO Detector InstancesID Failed to Start"
    print(failed_message)
    give_alert(failed_message)

def stopInstances(instancesIds):
  "call function to stop the ec2 instance"
  if(type(instancesIds) != list):  
    instancesIds = [instancesIds
    ]
  try:
    response = ec2.stop_instances(InstanceIds=instancesIds, DryRun=False)
    print("PTO Detector Instances Stopped")
  except ClientError as e:
    print(e)
    print(response)
    failed_message = "Alert : PTO Detector App InstancesID Failed to Stop"
    print(failed_message)

def check():
  for x in instances:
    retry = 0
    live = False
    for app_names in instances[x]:
      for app_details in app_names:
        if app_details=='webid':
          website_address = app_names[app_details]
        else :
          instance_id = app_names[app_details]
          
  
    print(date.today())
    print("Checking Webiste " + website_address)

    while(retry < 5):
      try:
        r = requests.get(website_address ,verify=True)
        if(r.status_code == 200):
          live = True
        break
      except: 
        print("Not Live, retry time " + str(retry + 1))
        print("Delaying request for " + str(DELAY_TIME) + " seconds...")
        retry += 1
        time.sleep(DELAY_TIME)

    if(live):
      
      print("Pass: Website is live")
      #startInstances(x)
      monitorInstances(instance_id)
      
    else:
      failed_message = "Alert: PTO Detector : https://practice-testing-ai-ml.qxf2.com/is-pto is dead/not reachable"
      print(r)
      print(failed_message)
      give_alert(failed_message)
       
      #stopInstances(x)   
    print("")

def main():
  check()

if __name__ == '__main__':
  main()