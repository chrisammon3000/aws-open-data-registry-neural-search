#! /usr/bin/bash

set -o allexport
source .env
set +o allexport

# $WEAVIATE_ENDPOINT is empty throw error
if [ -z "$WEAVIATE_ENDPOINT" ]; then
    echo "WEAVIATE_ENDPOINT not found in .env file. Please add it and try again."
    exit 1
fi

classes="Tutorial Publisher Dataset Resource ToolOrApplication Publication Service Tag"
for class in $classes; do
    curl -v -X DELETE $WEAVIATE_ENDPOINT/v1/schema/$class
done