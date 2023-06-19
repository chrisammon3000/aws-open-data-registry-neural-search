#! /usr/bin/bash

set -o allexport
source .env
set +o allexport

# $WEAVIATE_ENDPOINT is empty throw error
if [ -z "$WEAVIATE_ENDPOINT" ]; then
    echo "WEAVIATE_ENDPOINT not found in .env file. Please add it and try again."
    exit 1
fi

jq -c '.classes[]' "schema.json" | while read -r class; do
    curl \
        -X POST \
        -H "Content-Type: application/json" \
        -d "$class" \
        "$WEAVIATE_ENDPOINT/v1/schema"
    echo 
done
