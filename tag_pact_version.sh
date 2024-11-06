#!/bin/bash

PACT_BROKER_BASE_URL="http://127.0.0.1:8085"
PACT_BROKER_USERNAME="pactbroker"
PACT_BROKER_PASSWORD="pactbroker"
CONSUMER_NAME="UserServiceClient"
VERSION=$1
TAG=$2

# Check if version and tag are provided
if [ -z "$VERSION" ] || [ -z "$TAG" ]; then
  echo "Usage: ./tag_pact_version.sh <version> <tag>"
  exit 1
fi

# Tag the pact version in the broker
curl -u "${PACT_BROKER_USERNAME}:${PACT_BROKER_PASSWORD}" \
  -X PUT "${PACT_BROKER_BASE_URL}/pacts/provider/${PROVIDER_NAME}/consumer/${CONSUMER_NAME}/version/${VERSION}/tag/${TAG}"

echo "Tagged version ${VERSION} of ${CONSUMER_NAME} with '${TAG}'."