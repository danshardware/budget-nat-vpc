# this script is a kludge, but it works. 

import boto3
import pprint
import yaml

#import all the regions
ec2 = boto3.client('ec2')
response = ec2.describe_regions()
mappings = {"AWSAMIRegionMap":{}}
for region in response['Regions']:
#for region in [{"RegionName": "us-east-1"},{"RegionName": "us-east-2"}]:
    # search for ARM images for AMZ Linux 2
    ec2_request = boto3.client('ec2', region_name=region['RegionName'])
    print (region['RegionName'])
    arch = 'arm64'
    candidates = ec2_request.describe_images(
        Filters=[
            {'Name': 'virtualization-type', 'Values': ['hvm']},
            {'Name': 'architecture', 'Values': [arch]},
            {'Name': 'state', 'Values': ['available']},
            {'Name': 'root-device-type', 'Values': ['ebs']},
            {'Name': 'image-type', 'Values': ['machine']},
            {'Name': 'owner-alias', 'Values': ['amazon']},
            {'Name': 'name', 'Values': ['amzn2-ami-hvm-*']}
            ]
    )
    instanceType = "t4g"
    if len(candidates["Images"]) == 0:
        arch = 'x86_64'
        instanceType = "t3"
        candidates = ec2_request.describe_images(
            Filters=[
                {'Name': 'virtualization-type', 'Values': ['hvm']},
                {'Name': 'architecture', 'Values': [arch]},
                {'Name': 'state', 'Values': ['available']},
                {'Name': 'root-device-type', 'Values': ['ebs']},
                {'Name': 'image-type', 'Values': ['machine']},
                {'Name': 'owner-alias', 'Values': ['amazon']},
                {'Name': 'name', 'Values': ['amzn2-ami-hvm-*']}
                ]
        )
    #sort the candidates for the region
    if len(candidates["Images"]) != 0:
        candidates['Images'].sort(key=lambda x: x['CreationDate'], reverse=True)
        mappings["AWSAMIRegionMap"][region['RegionName']] = {"AMI": candidates['Images'][0]["ImageId"], "type": instanceType}

print()
print (yaml.dump({"Mappings": mappings}))
