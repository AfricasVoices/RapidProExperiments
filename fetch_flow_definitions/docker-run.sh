#!/bin/bash

set -e

IMAGE_NAME=fetch-flow-definitions

# Check that the correct number of arguments were provided.
if [[ $# -ne 2 ]]; then
    echo "Usage: ./docker-run.sh
    <google-cloud-credentials-file-path> <firestore-credentials-url>"
    exit
fi

# Assign the program arguments to bash variables.
GOOGLE_CLOUD_CREDENTIALS_FILE_PATH=$1
FIRESTORE_CREDENTIALS_URL=$2

# Build an image for this pipeline stage.
docker build -t "$IMAGE_NAME" .

CMD="pipenv run python -u fetch_flow_definitions.py /credentials/google-cloud-credentials.json \
    \"$FIRESTORE_CREDENTIALS_URL\"
"
container="$(docker container create -w /app "$IMAGE_NAME" /bin/bash -c "$CMD")"

function finish {
    # Tear down the container when done.
    docker container rm "$container" >/dev/null
}
trap finish EXIT

# Copy input data into the container
docker cp "$GOOGLE_CLOUD_CREDENTIALS_FILE_PATH" "$container:/credentials/google-cloud-credentials.json"

# Run the container
docker start -a -i "$container"
