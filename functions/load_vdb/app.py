import logging
import json
import yaml
import weaviate

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):

    logger.info(json.dumps(event))

    # process event
    for event_record in event['Records']:
        messages = json.loads(event_record['Sns']['Message'])
        for message in messages['Records']:
            print(message)




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
    with open('./functions/load_vdb/event.json') as file:
        event = json.load(file)
    context = ""
    lambda_handler(event, context)