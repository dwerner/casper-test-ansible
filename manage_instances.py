#!/usr/bin/env python3

import yaml
import boto3

ec2 = boto3.client('ec2')
response = ec2.describe_instances()
instance_names = {}

instance_prefix = "danw-test"

for reservation in response["Reservations"]:
    for instance in reservation["Instances"]:
        instance_id = instance["InstanceId"]
        for tag in instance["Tags"]:
            if tag["Key"] == "Name" and tag["Value"].startswith(instance_prefix):
                instance_names[instance_id] = tag["Value"]

if instance_names:
    print("The following instances were found with the prefix '{}':".format(instance_prefix))
    print(yaml.dump(instance_names))
else:
    print("Nothing to do")

answer = input("What would you like to do? [stop/start/CANCEL]")
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
    print("No valid option selected. Nothing to do.")
