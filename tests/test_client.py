"""pact test for user service client"""

import json
import logging
import os
import sys

import pytest
import requests
from requests.auth import HTTPBasicAuth

from pact_python_demo.client import UserClient
from pact import Consumer, Like, Provider, Term

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

PACT_UPLOAD_URL = (
    "http://127.0.0.1:8085/pacts/provider/UserService/consumer"
    "/UserServiceClient/version"
)
PACT_FILE = "userserviceclient-userservice.json"
PACT_BROKER_USERNAME = "pactbroker"
PACT_BROKER_PASSWORD = "pactbroker"

PACT_MOCK_HOST = 'localhost'
PACT_MOCK_PORT = 1234
PACT_DIR = os.path.dirname(os.path.realpath(__file__))

#The client fixture returns the UserClient instance to any test function that requires it
@pytest.fixture
def client():
    return UserClient(
        'http://{host}:{port}'
        .format(host=PACT_MOCK_HOST, port=PACT_MOCK_PORT)
    )


def push_to_broker(version):
    with open(os.path.join(PACT_DIR, PACT_FILE), 'rb') as pact_file:
        pact_file_json = json.load(pact_file)

    basic_auth = HTTPBasicAuth(PACT_BROKER_USERNAME, PACT_BROKER_PASSWORD)

    log.info("Uploading pact file to pact pactbroker...")

    r = requests.put(
        "{}/{}".format(PACT_UPLOAD_URL, version),
        auth=basic_auth,
        json=pact_file_json
    )
    if not r.ok:
        log.error("Error uploading: %s", r.content)
        r.raise_for_status()



#Configures the contract between the UserServiceClient (consumer) and UserService (provider), using Pact’s mock server
@pytest.fixture(scope='session')
def pact(request):
    pact = Consumer('UserServiceClient').has_pact_with(
        Provider('UserService'), host_name=PACT_MOCK_HOST, port=PACT_MOCK_PORT,
        pact_dir=PACT_DIR)
    #spins up a Pact mock server that listens for requests based on the defined contract interactions in each test
    pact.start_service()
    #Temporarily hands control back to the test, allowing each test case to define its expected interactions with the provider
    yield pact
    #shuts down the mock server once all tests that use the pact fixture have complete
    pact.stop_service()

    #for publishing/uploading the pact file to the pactbroker
    version = request.config.getoption('--publish-pact')

    if not request.node.testsfailed and version:
        push_to_broker(version)


def test_get_user_with_details(pact, client):
    expected = {
        'name': 'UserA',
        'id': '1234567',
        'admin': False,
        'contact': {
            'email': 'usera@example.com',
            'phone': '123-456-7890'
        },
        'address': {
            'street': '123 Main St',
            'city': 'Hometown',
            'state': 'CA',
            'zip': '12345'
        }
    }

    (pact
     .given('UserA exists and is not an administrator')
     .upon_receiving('a request for UserA with details')
     .with_request('get', '/users/UserA')
     .will_respond_with(200, body=Like(expected)))

    with pact:
        result = client.get_user('UserA')

    assert result == expected  # Assert the response matches expected


def test_get_non_existing_user(pact, client):
    (pact
     .given('UserA does not exist')
     .upon_receiving('a request for UserA')
     .with_request('get', '/users/UserA')
     .will_respond_with(404))

    with pact:
        result = client.get_user('UserA')

    assert result is None