import os
import logging
import json
import weaviate

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):

    logger.info(json.dumps(event))

    # # process event
    # for record in event['Records']:
    #     print("message")

    #     data = json.loads(record['body'])

            # logger.info(sns_message)

            # # load data
            # data = yaml.safe_load(sns_message)
            # logger.info(data)

            # # connect to weaviate
            # client = weaviate.Client("http://localhost:8080")

            # # create schema
            # schema = weaviate.Schema(client)
            # schema.create_class(data['class'])

            # # create object
            # objects = weaviate.Objects(client)
            # objects.create(data['class'], data['data'])

    return

if __name__ == "__main__":

    # open a json file
    path = os.path.join(os.path.dirname(__file__), 'event.json')
    with open(path) as file:
        event = json.load(file)
    context = ""
    lambda_handler(event, context)