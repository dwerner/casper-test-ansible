#!/usr/bin/env python3

import boto3
import yaml

ec2 = boto3.client('ec2')
response = ec2.describe_instances()
instance_names = {}
template_inventory = yaml.load(
    open("example-ansible-inventory.yaml"), Loader=yaml.FullLoader)


# use private ips for ansible connections
bootstrap = 1
# validators = 15
validators = 75
# zero_weight = 1
zero_weight = 225

instance_count = 0
bootstrap_hosts = template_inventory["all"]["children"]["bootstrap"]["hosts"] = {
}
validator_hosts = template_inventory["all"]["children"]["validators"]["hosts"] = {
}
zero_weight_hosts = template_inventory["all"]["children"]["zero_weight"]["hosts"] = {
}

for reservation in response["Reservations"]:
    print("reservation")

    for instance in reservation["Instances"]:

        instance_id = instance["InstanceId"]
        public_ip_addr = instance.get("PublicIpAddress")

        instance_state = instance['State']['Name']
        if public_ip_addr and instance_state == "running":
            for tag in instance["Tags"]:
                if tag["Key"] == "Name" and tag["Value"].startswith("danw-test"):
                    if instance_count < bootstrap:
                        print(instance_count, "bootstrap", public_ip_addr)
                        bootstrap_hosts[public_ip_addr] = ''
                    elif instance_count >= bootstrap and instance_count < bootstrap + validators:
                        print(instance_count, "validator", public_ip_addr)
                        validator_hosts[public_ip_addr] = ''
                    elif instance_count >= bootstrap + validators and instance_count < bootstrap + validators + zero_weight:
                        print(instance_count, "zero weight", public_ip_addr)
                        zero_weight_hosts[public_ip_addr] = ''

                    instance_count += 1

yaml.dump(template_inventory, open("generated-hosts.yaml", "w"))
print("all done, wrote ./generated-hosts.yaml", template_inventory)
