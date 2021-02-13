#!/usr/bin/env python3

import boto3

ec2 = boto3.client('ec2')
response = ec2.describe_instances()
instance_names = {}
for reservation in response["Reservations"]:
    for instance in reservation["Instances"]:
        instance_id = instance["InstanceId"]
        for tag in instance["Tags"]:
            if tag["Key"] == "Name" and tag["Value"].startswith("danw-test"):
                instance_names[instance_id] = tag["Value"]

if instance_names:
    print("The following instances will be stopped:", instance_names)
else:
    print("Nothing to do")

answer = input("Would you like to proceed with these changes? [stop/start/CANCEL]")
if answer == "start":
    print("Starting instances")
    ec2.start_instances(
        InstanceIds=list(instance_names.keys()),
    )
    print("All done.")
elif answer == "stop":
    print("Stopping instances")
    ec2.stop_instances(
        InstanceIds=list(instance_names.keys()),
    )
    print("All done.")
else:
    print("Nothing to do")
