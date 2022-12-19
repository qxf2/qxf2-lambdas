"""
This script contains the operations that can be performed on Raspberry
"""
import time
import traceback
import paramiko
import config


def run_command_in_pi(command, proxy_data, conn):
    "Connects to each device and executes a command"
    time_now = time.time()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    device_alias = proxy_data["device_alias"]

    try:
        ssh.connect(
            proxy_data["proxy_server"],
            username=config.PROXY_USERNAME,
            password=config.PROXY_PASSWORD,
            port=proxy_data["proxy_port"],
            banner_timeout=20,
        )
        ssh_command = verify_command_and_pick_correct_audio(ssh, command)

        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(ssh_command)
        print(
            "\nTime taken to ssh and run espeak for : "
            + device_alias
            + " : "
            + str(time.time() - time_now)
        )
        stdout = ssh_stdout.readlines()
        if len(stdout) > 0:
            print("\nStdout from " + device_alias + ": " + str(stdout))
        stderr = ssh_stderr.readlines()
        if len(stderr) > 0:
            print("\nStderr from " + device_alias + ": " + str(stderr))
    except Exception as error:
        print(
            "\nError while running espeak for "
            + device_alias
            + ", time taken: "
            + str(time.time() - time_now)
        )
        print(error)
        print(traceback.format_exc())
        conn.close()


def verify_command_and_pick_correct_audio(ssh, command):
    "Verify message and play correct audio"
    if "buddy" in command:
        run_sftp(ssh, "./audio_files/voiceDavid.wav")
        ssh_command = "aplay /home/pi/voiceDavid.wav"
    elif "0957" in command:
        run_sftp(ssh, "./audio_files/0957.wav")
        ssh_command = "aplay /home/pi/0957.wav"
    elif "1057" in command:
        run_sftp(ssh, "./audio_files/1057.wav")
        ssh_command = "aplay /home/pi/1057.wav"
    elif "1157" in command:
        run_sftp(ssh, "./audio_files/1157.wav")
        ssh_command = "aplay /home/pi/1157.wav"
    elif "1357" in command:
        run_sftp(ssh, "./audio_files/1357.wav")
        ssh_command = "aplay /home/pi/1357.wav"
    elif "1500" in command:
        run_sftp(ssh, "./audio_files/1500.wav")
        ssh_command = "aplay /home/pi/1500.wav"
    elif "1557" in command:
        run_sftp(ssh, "./audio_files/1557.wav")
        ssh_command = "aplay /home/pi/1557.wav"
    elif "1657" in command:
        run_sftp(ssh, "./audio_files/1657.wav")
        ssh_command = "aplay /home/pi/1657.wav"
    elif "1757" in command:
        run_sftp(ssh, "./audio_files/1757.wav")
        ssh_command = "aplay /home/pi/1757.wav"
    elif "1857" in command:
        run_sftp(ssh, "./audio_files/1857.wav")
        ssh_command = "aplay /home/pi/1857.wav"
    elif "1957" in command:
        run_sftp(ssh, "./audio_files/1957.wav")
        ssh_command = "aplay /home/pi/1957.wav"
    elif "2057" in command:
        run_sftp(ssh, "./audio_files/2057.wav")
        ssh_command = "aplay /home/pi/2057.wav"
    elif "2157" in command:
        run_sftp(ssh, "./audio_files/2157.wav")
        ssh_command = "aplay /home/pi/2157.wav"
    elif "2257" in command:
        run_sftp(ssh, "./audio_files/2257.wav")
        ssh_command = "aplay /home/pi/2257.wav"
    else:
        ssh_command = (
            "espeak -ven-us+f3 -s 125 --stdout '" + command + "' | aplay 2>/dev/null"
        )

    return ssh_command


def run_sftp(ssh, file_to_copy):
    "Copy files to the device"
    sftp = ssh.open_sftp()
    try:
        sftp.stat("/home/pi/" + file_to_copy)
        print("The file exists")
    except:
        file_name = file_to_copy.split("/")
        file_name = file_name[2]
        sftp.put(file_to_copy, "/home/pi/" + file_name)
        print("Copied the file")
