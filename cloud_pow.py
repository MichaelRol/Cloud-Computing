from pexpect import pxssh
import pexpect
import sys
import os
import boto3
import time

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
outfile.close()
instances = ec2.create_instances(
     ImageId='ami-0be057a22c63962cb',
     MinCount=1,
     MaxCount=1,
     InstanceType='t2.micro',
     KeyName='ec2-keypair',
     SecurityGroupIds=[
        'sg-0cfc311b8f3cb9bbc',
    ],
     
 )

instance = instances[0]
# Wait for the instance to enter the running state
instance.wait_until_running()

# Reload the instance attributes
instance.load()
dns = instance.public_dns_name
time.sleep(60)
try:
    # Upload Proof of Work code file
    scp = "scp -i 'ec2-keypair.pem' 'steps_pow.py' ubuntu@" + dns + ":/home/ubuntu/"
    term = pexpect.spawn("/bin/bash")
    term.sendline(scp)
    pexpect.run(scp)
    if len(sys.argv) > 2 or len(sys.argv) < 2:
        print("Yah dun it wrong")
    else:
        difficulty = int(sys.argv[1])
        child = pxssh.pxssh(timeout=1000, options={"StrictHostKeyChecking": "no"})
        child.login(dns, username="ubuntu", ssh_key="ec2-keypair.pem", auto_prompt_reset=False, port=22)
        command = "python3 steps_pow.py " + str(difficulty) + " 10"
        child.sendline(command)
        print(child.readline())
        print(child.readline())
        print(child.readline())
        child.sendline("exit")
finally:
    client.delete_key_pair(KeyName='ec2-keypair')
    os.remove("ec2-keypair.pem")
    client.terminate_instances(InstanceIds=[instance.id])