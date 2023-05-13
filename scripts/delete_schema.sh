#! /usr/bin/bash

set -o allexport
source .env
set +o allexport

# Create for loop: for class in Tutorial, Publisher, Dataset, Resource, ToolOrApplication, Publication
# execute curl -X DELETE http://52.203.73.188:8080/v1/schema/$class
classes="Tutorial Publisher Dataset Resource ToolOrApplication Publication Service Tag"
for class in $classes; do
    curl -v -X DELETE $WEAVIATE_ENDPOINT/v1/schema/$class
done