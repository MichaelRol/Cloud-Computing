import sys
import os
import boto3
import time
import paramiko
import pexpect
import uuid
import multiprocessing

def run_pow(difficulty, instance, start_val, end_val, key):

    instance = instances[0]
    # for instance in instances:
    # Wait for the instance to enter the running state
    instance.wait_until_running()
    # Reload the instance attributes
    instance.load()
    dns = instance.public_dns_name
    try:
        connection = False
        while connection == False:
            try:
                ssh_client=paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(dns, username="ubuntu", key_filename=os.path.expanduser(key+".pem"))
                connection = True
            except:
                time.sleep(5)
        ftp_client=ssh_client.open_sftp()
        ftp_client.put('steps_pow.py','/home/ubuntu/steps_pow.py')
        ftp_client.close()
        command = "python3 steps_pow.py " + str(difficulty) + " 10 " + str(start_val) + " " + str(end_val)
        stdin,stdout,stderr=ssh_client.exec_command(command)
        print(stdout.readlines())
    finally:
        end = time.time()
        print("Total time: " + str(end-start))
        client.delete_key_pair(KeyName=key)
        os.remove(keypem)
        client.terminate_instances(InstanceIds=[instance.id])

if __name__ == '__main__':
        
    if len(sys.argv) > 3 or len(sys.argv) < 3:
        print("Yah dun it wrong")
    else:
        difficulty = int(sys.argv[1])
        num_of_ec2s = int(sys.argv[2])

    start = time.time()

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
        MinCount=num_of_ec2s,
        MaxCount=num_of_ec2s,
        InstanceType='t2.micro',
        KeyName=key, 
        SecurityGroupIds=[
            'sg-0823d8a9cbaa125a1',
        ],
        
    )

    jobs = []
    range_size = 4294967296/num_of_ec2s
    start_val = 0
    for x in range(0, num_of_ec2s):
        instance = instances[x]
        if x == num_of_ec2s - 1:
            end_val = 4294967296
        else:
            end_val = start_val + range_size - 1         
        p = multiprocessing.Process(target=run_pow, args=(difficulty, instance, start_val, end_val, key,))
        jobs.append(p)
        p.start()
        start_val += range_size