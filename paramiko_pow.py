import sys
import os
import boto3
import time
import paramiko
import pexpect
import uuid

ec2 = boto3.resource('ec2')
client = boto3.client('ec2')
keyrand = str(uuid.uuid4())
key = 'ec2-keypair' + keyrand
keypem = key + ".pem"

# create a local file to store keypair
outfile = open(keypem,'w')

# use boto ec2 to create new keypair
key_pair = client.create_key_pair(KeyName=key)
# store keypair in a file
key_pair_to_write = str(key_pair['KeyMaterial'])

outfile.write(key_pair_to_write)
pexpect.run("chmod 400 "+ keypem)
outfile.close()
instances = ec2.create_instances(
     ImageId='ami-0be057a22c63962cb',
     MinCount=1,
     MaxCount=1,
     InstanceType='t2.micro',
     KeyName=key, 
     SecurityGroupIds=[
        'sg-0823d8a9cbaa125a1',
    ],
     
 )

instance = instances[0]
# Wait for the instance to enter the running state
instance.wait_until_running()

# Reload the instance attributes
instance.load()
dns = instance.public_dns_name
time.sleep(30)
try:
    if len(sys.argv) > 2 or len(sys.argv) < 2:
        print("Yah dun it wrong")
    else:
        difficulty = int(sys.argv[1])
        ssh_client=paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(dns, username="ubuntu", key_filename=os.path.expanduser(keypem))
        ftp_client=ssh_client.open_sftp()
        ftp_client.put('steps_pow.py','/home/ubuntu/steps_pow.py')
        ftp_client.close()
        command = "python3 steps_pow.py " + str(difficulty) + " 10"
        stdin,stdout,stderr=ssh_client.exec_command(command)
        print(stdout.readlines())
finally:
    client.delete_key_pair(KeyName=key)
    os.remove(keypem)
    client.terminate_instances(InstanceIds=[instance.id])
