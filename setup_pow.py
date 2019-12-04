import boto3
import json

print("Creating Key Pair")
key = 'ec2-keypair'
# # use boto ec2 to create new keypair

client = boto3.client('ec2')
try:
    key_pair = client.create_key_pair(KeyName=key)
    print("Key Pair Created")
except:
    print("Could not create keypair")

print('Creating SQS Queue')
sqs = boto3.resource('sqs')
queue = sqs.create_queue(QueueName='CloudComputingSQS')
print('Completed creating  SQS Queue')

print('Creating S3 Bucket')
s3 = boto3.client('s3')
try:
    s3.create_bucket(Bucket='cloudcomputing-pow',
        CreateBucketConfiguration={
            'LocationConstraint': 'eu-west-2'
        },)
except:
    print("Bucket already exists")

try:
    response = s3.upload_file('parallel_pow.py', 'cloudcomputing-pow', 'parallel_pow.py')
    print('S3 Bucket Created') 
except:
    print("Failed to upload to S3")

print('Creating IAM Instance Profile')

try:
    iam = boto3.client('iam')
    iam.create_instance_profile(
        InstanceProfileName='ec2_iam_role',
        Path='/'
    )
    print("IAM Instance Profile created")
except:
    print("IAM Instance Profile already exists")

path='/'
role_name='ec2_iam_role'
trust_policy={
    "Version": "2012-10-17",
    "Statement": [
        {
        "Sid": "",
        "Effect": "Allow",
        "Principal": {
            "Service": "ec2.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
        }
    ]
}

print("Creating IAM Role")
try:
    response = iam.create_role(
        Path=path,
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(trust_policy),
        MaxSessionDuration=3600,
    )

    iam.attach_role_policy(
        RoleName=role_name,
        PolicyArn='arn:aws:iam::aws:policy/AmazonEC2FullAccess'
    )
    iam.attach_role_policy(
        RoleName=role_name,
        PolicyArn='arn:aws:iam::aws:policy/AmazonSQSFullAccess'
    )
    iam.attach_role_policy(
        RoleName=role_name,
        PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess'
    )
    print("IAM Role Completed")
except Exception as e:
    print(e)

print("Adding role to instance profile")

try:
    iam.add_role_to_instance_profile(InstanceProfileName='ec2_iam_role', RoleName='ec2_iam_role')
    print("Role added to instance profile")
except:
    print("Role already added to instance Profile")
