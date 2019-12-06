import sys
import os
import boto3
import time
import random
import multiprocessing
import uuid

def add_tags(instances, x):
    instance = instances[x]
    # Wait for the instance to enter the running state
    tags = False
    while tags == False:
        try:
            instance.wait_until_running()
            tags = True
        except:
            time.sleep(1)
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

    sqs = boto3.resource('sqs')
    queue = sqs.create_queue(QueueName='CloudComputingSQS'+keyrand)

    sqs_client = boto3.client('sqs')
    try:
        queue_url = sqs_client.get_queue_url(
                QueueName='CloudComputingSQS'+keyrand
            )
    except:
        print("Failed to get SQS queue: have you ran setup_pow.py?")

    s3 = boto3.client('s3')
    try:
        s3.create_bucket(Bucket='cloudcomputing-pow'+keyrand,
            CreateBucketConfiguration={
                'LocationConstraint': 'eu-west-2'
            },)
    except:
        print("Bucket already exists")

    try:
        response = s3.upload_file('parallel_pow.py', 'cloudcomputing-pow'+keyrand, 'parallel_pow.py')
    except:
        print("Failed to upload to S3")
    instances=[]
    while instances == []:
        try:
            instances = ec2.create_instances(
                ImageId='ami-0e6107917072ee88c',
                MinCount=num_of_ec2,
                MaxCount=num_of_ec2,
                InstanceType='t2.micro',
                KeyName='ec2-keypair',
                UserData='''#!/bin/bash
                            cd ~
                            aws s3 cp s3://cloudcomputing-pow'''+keyrand+'''/parallel_pow.py .
                            python3 parallel_pow.py ''' + str(difficulty) + ' ' + queue_url['QueueUrl']
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
    queue = sqs.get_queue_by_name(QueueName='CloudComputingSQS'+keyrand)


    messages = []
    print("Waiting for golden nonce")
    while messages == []:
        messages = queue.receive_messages(WaitTimeSeconds=20)

    # print("Calc Time: " + messages[0].body + " Overhead: " + str(time.time() - start - float(messages[0].body)) + " Total: " + str(time.time() - start))
    print(messages[0].body)#+", "+str(time.time() - start - float(messages[0].body)) + ", " + str(time.time() - start))
    queue.delete()

    for job in jobs:
        job.terminate()

    s3_objects = s3.list_objects_v2(Bucket='cloudcomputing-pow'+keyrand)
    if "Contents" in s3_objects:
        for s3_obj in s3_objects["Contents"]:
            rm_obj = s3.delete_object(
            Bucket='cloudcomputing-pow'+keyrand, Key=s3_obj["Key"])
        s3.delete_bucket(Bucket='cloudcomputing-pow'+keyrand)
    ids = []
    for instance in instances:
        ids.append(instance.id)
    client.terminate_instances(InstanceIds=ids)