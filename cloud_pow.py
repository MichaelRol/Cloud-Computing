import sys
import os
import boto3
import time
import paramiko
import pexpect

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
time.sleep(30)
try:
    if len(sys.argv) > 2 or len(sys.argv) < 2:
        print("Yah dun it wrong")
    else:
        difficulty = int(sys.argv[1])
        ssh_client=paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(dns, username="ubuntu", key_filename=os.path.expanduser('ec2-keypair.pem'))
        except paramiko.ssh_exception.PasswordRequiredException:
            ssh_client.connect(dns, username="ubuntu", key_filename=os.path.expanduser('ec2-keypair.pem'))
        ftp_client=ssh_client.open_sftp()
        ftp_client.put('steps_pow.py','/home/ubuntu/steps_pow.py')
        ftp_client.close()
        command = "python3 steps_pow.py " + str(difficulty) + " 10"
        stdin,stdout,stderr=ssh_client.exec_command(command)
        print(stdout.readlines())
finally:
    client.delete_key_pair(KeyName='ec2-keypair')
    os.remove("ec2-keypair.pem")
    client.terminate_instances(InstanceIds=[instance.id])