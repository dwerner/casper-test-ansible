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
                instance_names[instance_id] = f"{tag['Value']} - {instance['State']['Name']}"

if instance_names:
    print(
        f"The following instances were found with the prefix '{instance_prefix}':")
    print(instance_names)
else:
    print("Nothing to do")

answer = input("What would you like to do? [stop/start/CANCEL]")
if answer == "start":
    count = int(input(f"How many? (of {len(instance_names)} instances):"))
    to_start = list([name for (name, state) in instance_names.items() if state.endswith('stopped')])[:count]
    print(f"Starting {count} instances")
    ec2.start_instances(
        InstanceIds=to_start,
    )
    print("All done.")
elif answer == "stop":
    to_stop = list([name for (name, state) in instance_names.items() if state.endswith('running')])
    print(f"Stopping {len(to_stop)} instances")
    ec2.stop_instances(
        InstanceIds=to_stop,
    )
    print("All done.")
else:
    print("No valid option selected. Nothing to do.")
