import hashlib
import sys
import time
import multiprocessing
import boto3
import pexpect

rank = -1

def find_golden_nonce(d, start_val, end_val, sqs_url):
    print("START: " + str(start_val), "END" + str(end_val))
    block = "COMSM0010cloud"
    block = bin(int.from_bytes(block.encode(), 'big'))
    binaryblock = block.replace("b", "")
    start = time.time()
    n = start_val  
    while n <  end_val:
        nonce = str(bin(n)).replace("0b", "")
        tohash = binaryblock + nonce
        h = hashlib.sha256()
        h.update(tohash.encode('ascii'))
        hash = h.hexdigest()
        h2 = hashlib.sha256()
        h2.update(hash.encode('ascii'))
        hashsq = h2.hexdigest()
        leadingz = 256-len(str(bin(int(hashsq, 16))[2:]))
        if leadingz >= d:
            end = time.time()
            # sqs.send_message(QueueUrl=sqs_url, MessageBody=str(end-start))
            sqs.send_message(QueueUrl=sqs_url, MessageBody=str(nonce)+" Calc Time: "+str(end-start))
            # print("Rank: " + str(rank) + ", Nonce: " + str(nonce) + ", Time: " + str(end - start))

            return
        n += 1
    print("No golden nonce found.")

if __name__ == '__main__':
    
    jobs = []      
    child = pexpect.spawn("/bin/bash")
    child.sendline("ec2-metadata -i")
    child.readline()
    child.expect("instance-id:")
    instance_id = str(child.readline()).split()[1]
    instance_id = instance_id.replace("b'", "")
    instance_id = instance_id.replace("'", "")
    instance_id = instance_id.replace("\\r\\n", "")
    sqs = boto3.client('sqs', region_name='eu-west-2')

    ec2 = boto3.resource('ec2', region_name='eu-west-2')
    instance = ec2.Instance(instance_id)
    while(rank == -1):
        for tag in instance.tags:
            if tag["Key"] == 'total':
                size = int(tag["Value"])
            if tag["Key"] == 'num':
                rank = int(tag["Value"])
    if len(sys.argv) > 3 or len(sys.argv) < 3:
        print("Usage: python3 steps_pow.py <difficulty level>  <SQS URL>.")
    else:
        try:
            difficulty = int(sys.argv[1])    
            sqs_url = sys.argv[2]
            if difficulty > 256:
                print("Difficulty value too large.")
                raise ValueError()
            if difficulty <= 0:
                print("Difficulty value must be positive integer.")
                raise ValueError()
            
            step = int(4294967296/size)
            start_val = rank * step
            end_val = start_val + step
            find_golden_nonce(difficulty, start_val, end_val, sqs_url)
        except ValueError:
            print("Usage: python3 steps_pow.py <difficulty level> <number of processes>.")



