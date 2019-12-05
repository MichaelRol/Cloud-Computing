import boto3

client = boto3.client('s3')
response = client.list_buckets()

for bucket in response['Buckets']:
    print(bucket['Name'])
    if bucket['Name'] == 'cloudcomputing-pow':
        continue
    s3_objects = client.list_objects_v2(Bucket=bucket["Name"])
    if "Contents" in s3_objects:
            for s3_obj in s3_objects["Contents"]:
                rm_obj = client.delete_object(
                    Bucket=bucket["Name"], Key=s3_obj["Key"])
    client.delete_bucket(Bucket=bucket['Name'])