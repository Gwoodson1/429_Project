"""Shared fixtures for the ECSE 429 Todo Manager REST API test suite."""
import os
import uuid
import xml.etree.ElementTree as ET

import pytest
import requests

BASE_URL = os.environ.get('TODO_API_URL', 'http://localhost:4567').rstrip('/')
TIMEOUT = 5


@pytest.fixture(scope='session')
def api():
    session = requests.Session()
    try:
        response = session.get(f'{BASE_URL}/todos', timeout=TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        session.close()
        pytest.fail(f'Todo Manager API is unavailable at {BASE_URL}: {exc}', pytrace=False)
    yield session
    session.close()


@pytest.fixture
def resources(api):
    """Track created objects and delete in reverse order even after assertion failures."""
    created = []

    def create(kind, **fields):
        response = api.post(f'{BASE_URL}/{kind}', json=fields, timeout=TIMEOUT)
        assert response.status_code == 201, (kind, response.status_code, response.text)
        item = response.json()
        assert 'id' in item, item
        created.append((kind, str(item['id'])))
        return item

    yield create

    for kind, item_id in reversed(created):
        try:
            api.delete(f'{BASE_URL}/{kind}/{item_id}', timeout=TIMEOUT)
        except requests.RequestException:
            pass


@pytest.fixture
def unique_title():
    return f'ECSE429 pytest {uuid.uuid4().hex[:12]}'


def call(api, method, path, **kwargs):
    return api.request(method, f'{BASE_URL}{path}', timeout=TIMEOUT, **kwargs)


def json_items(response, collection):
    assert response.status_code == 200, (response.status_code, response.text)
    body = response.json()
    assert collection in body, body
    assert isinstance(body[collection], list)
    return body[collection]


def xml_root(response):
    assert response.status_code == 200, (response.status_code, response.text)
    return ET.fromstring(response.content)
