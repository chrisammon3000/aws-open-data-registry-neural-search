import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv());
import json
import boto3

ssm = boto3.client('ssm', region_name=os.environ['CDK_DEFAULT_REGION'])

root_dir = Path(__file__).parent.parent.parent

with open(root_dir / "config.json") as f:
    config = json.load(f)

ORGANIZATION = config["tags"]["org"]
APP_NAME = config["tags"]["app"]

WEAVIATE_ENDPOINT = ssm.get_parameter(Name=f"/{ORGANIZATION}/{APP_NAME}/WeaviateEndpoint")['Parameter']['Value']
