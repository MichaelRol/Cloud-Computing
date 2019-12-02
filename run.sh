#!/bin/bash
yum install -y python3-pip python3 python3-setuptools
yum update
cd ~
aws s3 cp s3://cloudcomputing-pow/parallel_pow.py .
pip3 install boto3
python3 parallel_pow.py 18 2
