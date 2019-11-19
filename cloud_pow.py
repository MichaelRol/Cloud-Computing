import pexpect 
import sys
import boto3

if len(sys.argv) > 2 or len(sys.argv) < 2:
    print("Yah dun it wrong")
else:
    difficulty = int(sys.argv[1])
    child = pexpect.spawn("/bin/bash")
    child.sendline("ssh -i ~/.ssh/CloudCOmp.pem ubuntu@ec2-3-8-48-186.eu-west-2.compute.amazonaws.com")
    child.expect("Last login")
    child.readline()
    command = "python3 steps_pow.py " + str(difficulty) + " 10"
    child.sendline(command)
    child.readline()
    print(child.readline())
    child.sendline("exit")