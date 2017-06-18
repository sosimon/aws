import boto3

sg_id = "sg-7d482705"
ec2 = boto3.resource("ec2")
sg = ec2.SecurityGroup(sg_id)

bucket_name = "simonso-access-control"
file_name = "ip_whitelist"
s3 = boto3.resource("s3")

def lambda_handler(event, context):
    # Read rules list from S3 bucket 
    obj = s3.Object(bucket_name, file_name)
    content = obj.get()["Body"].read()
    desired_rules = content.strip("\n").split("\n")
    print desired_rules

    # Get existing list of rules from security group
    actual_rules = []
    for p in sg.ip_permissions:
        for cidr_ip in p["IpRanges"]:
            actual_rules.append(",".join([p["IpProtocol"], str(p["FromPort"]), str(p["ToPort"]), cidr_ip["CidrIp"]]))
    print actual_rules

    # Remove rules not in desired_rules
    for rule in actual_rules:
        if rule not in desired_rules:
            print "Removing rule: %s" % rule 
            r = rule.split(",")
            sg.revoke_ingress(IpProtocol=r[0],FromPort=int(r[1]),ToPort=int(r[2]),CidrIp=r[3])

    # Add rules not in actual_rules
    for rule in desired_rules:
        if rule not in actual_rules:
            print "Adding rule: %s" % rule
            r = rule.split(",")
            sg.authorize_ingress(IpProtocol=r[0],FromPort=int(r[1]),ToPort=int(r[2]),CidrIp=r[3])


