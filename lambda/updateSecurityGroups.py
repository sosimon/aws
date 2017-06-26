import boto3
import re

ec2 = boto3.resource("ec2")

s3 = boto3.resource("s3")
bucket_name = "simonso-access-control"
bucket = s3.Bucket(bucket_name)


def lambda_handler(event, context):
    # Get list of security groups
    sg_ids = [ sg.id for sg in ec2.security_groups.all() ]

    for obj in bucket.objects.all():
        filename = obj.key

        # Make sure, at the very least, the filenames match the pattern of a security group id
        # otherwise, move on to the next file
        if not re.match(r'^sg-[a-z0-9]{8}$', filename):
            print '%s does not match the security group id pattern' % filename
            continue

        # Check if filename matches any of the security groups, if not, move on
        if filename not in sg_ids:
            print 'Security group %s not found' % filename
            continue

        # Read rules list from S3 bucket
        content = obj.get()["Body"].read()
        desired_rules = content.strip("\n").split("\n")
        print desired_rules

        sg = ec2.SecurityGroup(filename)

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


