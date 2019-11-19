from pexpect import pxssh
import sys
import boto3

if len(sys.argv) > 2 or len(sys.argv) < 2:
    print("Yah dun it wrong")
else:
    difficulty = int(sys.argv[1])
    child = pxssh.pxssh(timeout=1000, options={"StrictHostKeyChecking": "no"})
    child.login("ec2-3-10-242-69.eu-west-2.compute.amazonaws.com", username="ubuntu", ssh_key="~/.ssh/CloudCOmp.pem")
    command = "python3 steps_pow.py " + str(difficulty) + " 10"
    child.sendline(command)
    child.readline()
    print(child.readline())
    child.sendline("exit")