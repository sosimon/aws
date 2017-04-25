import boto3

ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    filters = [
        {'Name': 'tag:Name', 'Values': 'interview-demo'},
        {'Name': 'instance-state-name', 'Values': ['pending', 'running',
        'shutting-down', 'stopping', 'stopped']},
    ]
    response = ec2.describe_instances(Filters=filters)

    for reserv in response['Reservations']:
        for inst in reserv['Instances']:
            print "Terminating instance %s" % inst['InstanceId']
            ec2.terminate_instances(InstanceIds=[inst['InstanceId']])
