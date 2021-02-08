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

operations = []
for num, (instance_id, old_name) in enumerate(instance_names.items()):
    name = "danw-test-{0:03d}".format(num)
    if old_name != name:
        operations.append((instance_id, {"Key":"Name", "Value": name }))

if operations:
    print("The following tags will be created:", operations)
else:
    print("Nothing to do, all instances match desired naming scheme")

answer = input("Would you like to proceed with these changes? [y/N]")
if answer == "y":
    for instance_id, tag in operations:
        ec2.create_tags(Resources=[instance_id], Tags=[tag])

print("All done.")
