import sys
import os
import boto3
import time
import pexpect
import random
import multiprocessing
import uuid
from pexpect import pxssh

def add_tags(instances, x):
    instance = instances[x]
    # Wait for the instance to enter the running state
    instance.wait_until_running()
    # instance.load()
    instance.create_tags(Tags=[{'Key': 'num', 
                                    'Value': str(x)},])

if __name__ == '__main__':
    difficulty = 0

    if len(sys.argv) > 3 or len(sys.argv) < 3:
        print("Yah dun it wrong")
        sys.exit()
    else:
        difficulty = int(sys.argv[1])
        num_of_ec2 = int(sys.argv[2])

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
    pexpect.run("chmod 400 " + keypem)
    outfile.close()

    sqs = boto3.resource('sqs')

    sqs_client = boto3.client('sqs')
    try:
        queue_url = sqs_client.get_queue_url(
                QueueName='CloudComputingSQS'
            )
    except:
        print("Failed to get SQS queue: have you ran setup_pow.py?")

    instances=[]
    while instances == []:
        try:
            instances = ec2.create_instances(
                ImageId='ami-0e6107917072ee88c',
                MinCount=num_of_ec2,
                MaxCount=num_of_ec2,
                InstanceType='t2.micro',
                KeyName=key, 
                SecurityGroupIds=[
                    'sg-0823d8a9cbaa125a1',
                ],
                UserData='''#!/bin/bash
                            cd ~
                            aws s3 cp s3://cloudcomputing-pow/parallel_pow.py .
                            python3 parallel_pow.py ''' + str(difficulty) + " 4 " + queue_url['QueueUrl']
                            ,
                IamInstanceProfile={'Name': 'ec2_iam_role'},
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {
                                'Key': 'total',
                                'Value': str(num_of_ec2)
                            },
                            {
                                'Key': 'num',
                                'Value': str(-1)
                            },
                        ]
                    },
                ],
                
            )
        except:
            time.sleep(5)
    jobs = []
    for x in range(0, num_of_ec2):
        try:
            p = multiprocessing.Process(target=add_tags, args=(instances, x,))
            jobs.append(p)
            p.start()
        except:
            print("Failed to create a process")

    # Get the queue
    queue = sqs.get_queue_by_name(QueueName='CloudComputingSQS')


    messages = []
    print("Waiting for message")
    try:
        while messages == []:
            messages = queue.receive_messages(WaitTimeSeconds=20)

        print("Nonce: " + messages[0].body + " Time taken: " + str(time.time() - start))
    finally:
        for job in jobs:
            job.join()
        client.delete_key_pair(KeyName=key)
        os.remove(keypem)
        ids = []
        for instance in instances:
            ids.append(instance.id)
        client.terminate_instances(InstanceIds=ids)
    queue.purge()