#!/bin/bash

PACT_BROKER_BASE_URL="http://127.0.0.1:8085"
PACT_BROKER_USERNAME="pactbroker"
PACT_BROKER_PASSWORD="pactbroker"
PACT_PROVIDER_VERSION=$1  # Pass the version for tracking

# Check if the version argument is provided
if [ -z "$PACT_PROVIDER_VERSION" ]; then
  echo "Please provide a provider version (e.g., './verify_pact.sh 1.0.0')"
  exit 1
fi

# Verify pacts
PACT_URL="${PACT_BROKER_BASE_URL}/pacts/provider/UserService/consumer/UserServiceClient/latest"
pact-verifier --provider-base-url=http://localhost:5000 \
  --pact-broker-base-url=$PACT_BROKER_BASE_URL \
  --pact-broker-username=$PACT_BROKER_USERNAME \
  --pact-broker-password=$PACT_BROKER_PASSWORD \
  --provider-app-version=$PACT_PROVIDER_VERSION

echo "Pact verification completed!"