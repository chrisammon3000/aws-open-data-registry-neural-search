import os
import logging
from typing import Dict
from datetime import datetime
from uuid import uuid4
import json
import boto3
import yaml

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DATA_INGEST_TOPIC_ARN = os.environ['DATA_INGEST_TOPIC_ARN']

s3 = boto3.client('s3')
sns = boto3.client('sns')

def lambda_handler(event, context):

    logger.info(json.dumps(event))

    for record in event['Records']:

        # get bucket name and key
        bucket_name = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        # get the object from S3
        s3_object = s3.get_object(Bucket=bucket_name, Key=key)
        s3_object_body = s3_object['Body'].read().decode('utf-8')
        dataset = yaml.safe_load(s3_object_body)

        # build payload
        payload = {
            "created_at_utc": datetime.strptime(event['Records'][0]['eventTime'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M:%S.%f%z")[:-3],
            "data": dataset
        }

        # publish the dataset to the SNS topic
        sns.publish(
            TopicArn=DATA_INGEST_TOPIC_ARN,
            Message=json.dumps(payload)
        )

    return


if __name__ == "__main__":

    # open a json file
    path = os.path.join(os.path.dirname(__file__), 'event.json')
    with open(path) as file:
        event = json.load(file)
    context = ""
    lambda_handler(event, context)