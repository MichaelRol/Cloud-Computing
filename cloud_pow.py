from pexpect import pxssh
import pexpect
import sys
import os
import boto3

ec2 = boto3.resource('ec2')
client = boto3.client('ec2')

# create a local file to store keypair
outfile = open('ec2-keypair.pem','w')

# use boto ec2 to create new keypair
key_pair = ec2.create_key_pair(KeyName='ec2-keypair')

# store keypair in a file
key_pair_to_write = str(key_pair.key_material)
outfile.write(key_pair_to_write)
pexpect.run("chmod 400 ec2-keypair.pem")

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

response = client.delete_key_pair(KeyName='ec2-keypair')
os.remove("ec2-keypair.pem")