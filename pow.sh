aws ec2 run-instances --image-id ami-0be057a22c63962cb --count 1 --instance-type t2.micro --key-name CloudCOmp -filepath CloudCOmp.pem --security-groups my-sg

run script on pre-existing ec2 instance
create ec2 with pre existing security group
create security group then ec2 then run program