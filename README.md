# Cloud-Computing
Repository for storing coursework for the University of Bristol COMSM0010 Cloud Computing which is a system for generating Blockchain style, Proof of Work golden nonces.

## Prerequisits 

- Python3 `sudo apt-get install python3`
- pip3  `sudo apt install python3-pip`
- Boto3 `sudo pip3 install boto3`
- AWS CLI `sudo pip3 install aws-cli`

- You must run `aws configure` and enter the access key id and secret access key of an IAM user with programmatic access to your account and eith Adminastrator access rights, or AmazonEC2FullAccess, AmazonS3FullAccess, AmazonSQSFullAccess and IAMFullAccess. You must also enter an AWS region for the system to be run on, eu-west-2 is recommend.

## Execution

- First run `python3 setup_pow.py`
- Once that has completed run `python3 cloud_pow.py <difficulty level> <number of EC2 instances to create>` to generate a golden nonce with the given difficulty level.
