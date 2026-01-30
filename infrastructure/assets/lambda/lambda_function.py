import json
import boto3
import urllib3
import pymysql
import os

http = urllib3.PoolManager()

def send_response(event, context, status, data):
    response_body = {
        "Status": status,
        "Reason": f"See details in CloudWatch Log Stream: {context.log_stream_name}",
        "PhysicalResourceId": context.log_stream_name,
        "StackId": event["StackId"],
        "RequestId": event["RequestId"],
        "LogicalResourceId": event["LogicalResourceId"],
        "Data": data,
    }
    json_response = json.dumps(response_body)
    headers = {"Content-Type": "application/json"}
    http.request("PUT", event["ResponseURL"], body=json_response, headers=headers)

def get_secret():
    client = boto3.client("secretsmanager")
    resp = client.get_secret_value(
        SecretId=os.environ["DB_SECRET_NAME"]
    )

    secret = json.loads(resp["SecretString"])
    return secret["password"]

def lambda_handler(event, context):
    print("Event:", json.dumps(event))

    # Only run on Create
    if event["RequestType"] != "Create":
        return send_response(event, context, "SUCCESS", {})

    try:
        s3 = boto3.client("s3")

        sql = s3.get_object(
            Bucket=os.environ["SQL_BUCKET"],
            Key=os.environ["SQL_KEY"]
        )["Body"].read().decode()

        conn = pymysql.connect(
            host=os.environ["DB_HOST"],
            user=os.environ["DB_USER"],
            password=get_secret(),
            database=os.environ["DB_NAME"],
            client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS
        )

        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()

        cur.close()
        conn.close()

    except Exception as e:
        print("Error:", str(e))
        return send_response(event, context, "FAILED", {"Error": str(e)})

    return send_response(event, context, "SUCCESS", {})
