import string
import random

def lambda_handler(event, context):
    l = 32
    if "queryStringParameters" in event:
        queryString = event["queryStringParameters"]
        if isinstance(queryString, dict) and "length" in queryString.keys():
            l = queryString['length']
            if not isinstance(l, int):
                l = int(l)
                resp = {
                    "statusCode": 200,
                    "headers": {
                        "Access-Control-Allow-Origin": "*"
                    },
                    "body": ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in xrange(l))
                }
                return resp
