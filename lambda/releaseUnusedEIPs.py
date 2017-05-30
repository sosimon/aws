import boto3

ec2 = boto3.client("ec2")
def lambda_handler(event, context):
    response = ec2.describe_addresses()
    eips = response["Addresses"]
    eips_notused = [ eip for eip in eips if "AssociationId" not in eip]
    for eip in eips_notused:
        print "Releasing EIP: %s" % eip["PublicIp"]
        res = ec2.release_address(AllocationId=eip["AllocationId"])
        print res
