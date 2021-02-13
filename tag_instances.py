#!/usr/bin/env python3

import boto3
import yaml

ec2 = boto3.client('ec2')
response = ec2.describe_instances()
instance_names = {}
instance_ips = {}
for reservation in response["Reservations"]:
    for instance in reservation["Instances"]:
        instance_id = instance["InstanceId"]
        instance_ip_addr = instance.get("PublicIpAddress")
        if instance_ip_addr:
            for tag in instance["Tags"]:
                if tag["Key"] == "Name" and tag["Value"].startswith("danw-test"):
                    instance_names[instance_id] = tag["Value"]
                    instance_ips[instance_id] = instance_ip_addr

operations = {}
for instance_id, old_name in instance_ips.items():
    name = "danw-test-{}".format(instance_ips[instance_id])
    if old_name != name:
        operations[instance_id] = {"Key":"Name", "Value": name }

if operations:
    print("The following tags will be created:")
    print(yaml.dump(operations))
else:
    print("Nothing to do, all instances match desired naming scheme")

answer = input("Would you like to proceed with these changes? [y/N]")
if answer == "y":
    for instance_id, tag in operations.items():
        ec2.create_tags(
            Resources=[instance_id],
            Tags=[tag]
        )
    print("All done.")
else:
    print("Nothing to do")
