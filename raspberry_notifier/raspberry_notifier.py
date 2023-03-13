"""
Lambda to connect to raspberry pi using remote.it.
All devices must be registered with remote.it account.
It will connect to all online devices and play out an audio message.
"""

from multiprocessing import Pipe, Process
from skype_sender import send_skype_message
from remoteit_helper import list_devices, connect_and_run


def run_in_parallel(command):
    "Makes connections to different devices in parallel"
    parent_connections = []
    processes = []
    device_address_alias_dict = list_devices()
    for device_address in device_address_alias_dict:
        device_alias = device_address_alias_dict[device_address]
        parent_conn, child_conn = Pipe()
        parent_connections.append(parent_conn)
        # create the process, pass instance and connection
        process = Process(
            target=connect_and_run,
            args=(command, device_address, device_alias, child_conn),
        )
        processes.append(process)
    for process in processes:
        process.start()
    for process in processes:
        process.join()


def trigger_notifications(event, context):
    "lambda entry point"
    TRIGGER_COMMAND = event['msg']
    run_in_parallel(TRIGGER_COMMAND)
    if "buddy" in TRIGGER_COMMAND:
        send_skype_message(TRIGGER_COMMAND)
        TRIGGER_COMMAND = (
            TRIGGER_COMMAND + "https://water-cooler-talks.qxf2.com/water-cooler-talks"
        )
