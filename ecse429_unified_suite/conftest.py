"""Shared fixtures for the ECSE 429 Todo Manager REST API test suite."""
import os
import uuid
import xml.etree.ElementTree as ET

import pytest
import requests
from pytest_bdd import given, parsers, then, when

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
def resource_state():
    return {'last_response': None, 'created': []}


@pytest.fixture
def resources(api, resource_state):
    """Track created objects and delete in reverse order even after assertion failures."""
    created = resource_state['created']

    def create(kind, **fields):
        response = api.post(f'{BASE_URL}/{kind}', json=fields, timeout=TIMEOUT)
        resource_state['last_response'] = response
        _track_created_response(resource_state, kind, response)
        assert response.status_code == 201, (kind, response.status_code, response.text)
        item = response.json()
        assert 'id' in item, item
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


@pytest.fixture
def bdd_state():
    return {}


def _collection(entity):
    collections = {'todo': 'todos', 'category': 'categories'}
    assert entity in collections, f'Unsupported story entity: {entity}'
    return collections[entity]


def _track_created_response(state, entity, response):
    if response.status_code == 201:
        item = response.json()
        if isinstance(item, dict) and 'id' in item:
            collections = {
                'todo': 'todos',
                'todos': 'todos',
                'category': 'categories',
                'categories': 'categories',
                'projects': 'projects',
            }
            assert entity in collections, f'Unsupported resource type: {entity}'
            state['created'].append((collections[entity], str(item['id'])))


def _create_story_entity(resources, state, entity, title, description=None, done=False):
    unique_title = f'{title} [{uuid.uuid4().hex[:10]}]'
    fields = {'title': unique_title}
    if description is not None:
        fields['description'] = description
    if entity == 'todo':
        fields['doneStatus'] = done
    item = resources(_collection(entity), **fields)
    state[f'{entity}_item'] = item
    state[f'{entity}_title'] = unique_title
    state[f'{entity}_example_title'] = title
    return item


def _assert_story_title(state, entity, title):
    assert title == state[f'{entity}_example_title'], (
        f'Expected {entity} example title {state[f"{entity}_example_title"]!r}, got {title!r}'
    )


def _get_story_entity(api, state, entity):
    item = state[f'{entity}_item']
    response = call(api, 'GET', f"/{_collection(entity)}/{item['id']}")
    found = json_items(response, _collection(entity))
    assert len(found) == 1, found
    return found[0]


@given('the Todo Manager API is available')
def todo_manager_api_is_available(api):
    return api


@given('the test environment is prepared')
def test_environment_is_prepared(resources):
    assert callable(resources)


@given(parsers.parse('a {entity:w} titled "{title}" exists'))
def story_entity_exists(resources, bdd_state, entity, title):
    _create_story_entity(resources, bdd_state, entity, title, description='Initial description')


@given(parsers.parse('a completed todo titled "{title}" exists'))
def completed_todo_exists(resources, bdd_state, title):
    _create_story_entity(
        resources, bdd_state, 'todo', title, description='Initial description', done=True
    )


@given(parsers.parse('a todo titled "{todo_title}" and category titled "{category_title}" exist'))
def todo_and_category_exist(resources, bdd_state, todo_title, category_title):
    _create_story_entity(resources, bdd_state, 'todo', todo_title, description='Initial description')
    _create_story_entity(resources, bdd_state, 'category', category_title, description='Initial description')


@given(parsers.parse('a todo titled "{todo_title}" is assigned to category titled "{category_title}"'))
def todo_is_assigned_to_category(api, resources, bdd_state, todo_title, category_title):
    todo_and_category_exist(resources, bdd_state, todo_title, category_title)
    todo = bdd_state['todo_item']
    category = bdd_state['category_item']
    response = call(
        api, 'POST', f"/todos/{todo['id']}/categories", json={'id': str(category['id'])}
    )
    assert response.status_code == 201, response.text


@given(parsers.parse('a category titled "{category_title}" already contains todo "{todo_title}"'))
def category_contains_todo(api, resources, bdd_state, todo_title, category_title):
    todo_and_category_exist(resources, bdd_state, todo_title, category_title)
    todo = bdd_state['todo_item']
    category = bdd_state['category_item']
    response = call(
        api, 'POST', f"/categories/{category['id']}/todos", json={'id': str(todo['id'])}
    )
    assert response.status_code == 201, response.text


@when(parsers.parse('I create a {entity:w} titled "{title}" with description "{description}"'))
def create_story_entity(resources, resource_state, bdd_state, entity, title, description):
    _create_story_entity(resources, bdd_state, entity, title, description=description)
    bdd_state['response'] = resource_state['last_response']


@when(parsers.parse('I create a {entity:w} titled "{title}" without a description'))
def create_story_entity_without_description(resources, resource_state, bdd_state, entity, title):
    _create_story_entity(resources, bdd_state, entity, title)
    bdd_state['response'] = resource_state['last_response']


@when(parsers.parse('I create a {entity:w} without a title but with description "{description}"'))
def create_story_entity_without_title(api, resource_state, bdd_state, entity, description):
    fields = {'description': description}
    if entity == 'todo':
        fields['doneStatus'] = False
    response = call(api, 'POST', f'/{_collection(entity)}', json=fields)
    _track_created_response(resource_state, entity, response)
    bdd_state['response'] = response


@when(parsers.parse('I retrieve the {entity:w} titled "{title}" as JSON'))
def retrieve_story_entity_as_json(api, bdd_state, entity, title):
    _assert_story_title(bdd_state, entity, title)
    item = bdd_state[f'{entity}_item']
    bdd_state['response'] = call(api, 'GET', f"/{_collection(entity)}/{item['id']}")


@when(parsers.parse('I retrieve the {entity:w} titled "{title}" as XML'))
def retrieve_story_entity_as_xml(api, bdd_state, entity, title):
    _assert_story_title(bdd_state, entity, title)
    item = bdd_state[f'{entity}_item']
    bdd_state['response'] = call(
        api,
        'GET',
        f"/{_collection(entity)}/{item['id']}",
        headers={'Accept': 'application/xml'},
    )


@when(parsers.parse('I retrieve a missing {entity:w} with ID "{item_id}"'))
def retrieve_missing_story_entity(api, bdd_state, entity, item_id):
    bdd_state['response'] = call(api, 'GET', f'/{_collection(entity)}/{item_id}')


@when(parsers.parse('I change the {entity:w} titled "{title}" description to "{description}" using POST'))
def post_story_entity_description(api, bdd_state, entity, title, description):
    _assert_story_title(bdd_state, entity, title)
    item = bdd_state[f'{entity}_item']
    bdd_state['response'] = call(
        api, 'POST', f"/{_collection(entity)}/{item['id']}", json={'description': description}
    )


@when(parsers.parse(
    'I replace the {entity:w} titled "{title}" with title "{new_title}" and description "{description}" using PUT'
))
def put_story_entity(api, bdd_state, entity, title, new_title, description):
    _assert_story_title(bdd_state, entity, title)
    item = bdd_state[f'{entity}_item']
    fields = {'title': new_title, 'description': description}
    if entity == 'todo':
        fields['doneStatus'] = True
    bdd_state['response'] = call(api, 'PUT', f"/{_collection(entity)}/{item['id']}", json=fields)
    bdd_state[f'{entity}_example_title'] = new_title
    bdd_state[f'{entity}_title'] = new_title


@when(parsers.parse('I try to replace the {entity:w} titled "{title}" with a PUT payload missing its title'))
def put_story_entity_without_title(api, bdd_state, entity, title):
    _assert_story_title(bdd_state, entity, title)
    item = bdd_state[f'{entity}_item']
    bdd_state['response'] = call(
        api, 'PUT', f"/{_collection(entity)}/{item['id']}", json={'description': 'Should not apply'}
    )


@then(parsers.parse('the response status should be {status:d}'))
def response_status_should_be(bdd_state, status):
    response = bdd_state['response']
    assert response.status_code == status, (response.status_code, response.text)


@then(parsers.parse('the {entity:w} titled "{title}" should exist'))
def story_entity_should_exist(api, bdd_state, entity, title):
    _assert_story_title(bdd_state, entity, title)
    found = _get_story_entity(api, bdd_state, entity)
    assert found['title'] == bdd_state[f'{entity}_title']


@then(parsers.parse('the {entity:w} titled "{title}" should appear in the response'))
def story_entity_should_appear_in_response(bdd_state, entity, title):
    _assert_story_title(bdd_state, entity, title)
    response = bdd_state['response']
    body = response.json()
    collection = _collection(entity)
    items = body.get(collection, []) if isinstance(body, dict) else body
    assert any(item.get('title') == bdd_state[f'{entity}_title'] for item in items), body


@then(parsers.parse('the response should contain XML for the {entity:w} titled "{title}"'))
def xml_response_should_contain_story_entity(bdd_state, entity, title):
    _assert_story_title(bdd_state, entity, title)
    response = bdd_state['response']
    assert 'xml' in response.headers.get('Content-Type', '').lower()
    root = ET.fromstring(response.content)
    assert any(element.text == bdd_state[f'{entity}_title'] for element in root.iter('title'))


@then(parsers.parse('the {entity:w} titled "{title}" should have description "{description}"'))
def story_entity_should_have_description(api, bdd_state, entity, title, description):
    _assert_story_title(bdd_state, entity, title)
    found = _get_story_entity(api, bdd_state, entity)
    assert found['title'] == bdd_state[f'{entity}_title']
    assert found['description'] == description


@then(parsers.parse('the todo titled "{title}" should be marked complete'))
def todo_should_be_complete(api, bdd_state, title):
    _assert_story_title(bdd_state, 'todo', title)
    found = _get_story_entity(api, bdd_state, 'todo')
    assert str(found['doneStatus']).lower() == 'true'


@when(parsers.parse('I delete the {entity:w} titled "{title}"'))
def delete_story_entity(api, bdd_state, entity, title):
    _assert_story_title(bdd_state, entity, title)
    item = bdd_state[f'{entity}_item']
    bdd_state['response'] = call(api, 'DELETE', f"/{_collection(entity)}/{item['id']}")


@when(parsers.parse('I delete a missing {entity:w} with ID "{item_id}"'))
def delete_missing_story_entity(api, bdd_state, entity, item_id):
    bdd_state['response'] = call(api, 'DELETE', f'/{_collection(entity)}/{item_id}')


@then(parsers.parse('the {entity:w} titled "{title}" should no longer exist'))
def story_entity_should_no_longer_exist(api, bdd_state, entity, title):
    _assert_story_title(bdd_state, entity, title)
    item = bdd_state[f'{entity}_item']
    response = call(api, 'GET', f"/{_collection(entity)}/{item['id']}")
    assert response.status_code == 404, (response.status_code, response.text)


@then(parsers.parse('the todo titled "{title}" should still be retrievable'))
def todo_should_still_be_retrievable(api, bdd_state, title):
    _assert_story_title(bdd_state, 'todo', title)
    item = bdd_state['todo_item']
    response = call(api, 'GET', f"/todos/{item['id']}")
    assert response.status_code == 200, (response.status_code, response.text)


@when('I assign the todo to the category')
def assign_todo_to_category(api, bdd_state):
    todo = bdd_state['todo_item']
    category = bdd_state['category_item']
    bdd_state['response'] = call(
        api, 'POST', f"/todos/{todo['id']}/categories", json={'id': str(category['id'])}
    )


@when('I assign a missing category to the todo')
def assign_missing_category_to_todo(api, bdd_state):
    todo = bdd_state['todo_item']
    bdd_state['response'] = call(
        api, 'POST', f"/todos/{todo['id']}/categories", json={'id': '999999999'}
    )


@when('I remove the category from the todo')
def remove_category_from_todo(api, bdd_state):
    todo = bdd_state['todo_item']
    category = bdd_state['category_item']
    bdd_state['response'] = call(
        api, 'DELETE', f"/todos/{todo['id']}/categories/{category['id']}"
    )


@then('the todo should list the category')
def todo_should_list_category(api, bdd_state):
    todo = bdd_state['todo_item']
    category = bdd_state['category_item']
    items = json_items(call(api, 'GET', f"/todos/{todo['id']}/categories"), 'categories')
    assert any(str(item['id']) == str(category['id']) for item in items), items


@then('the todo should not list the category')
def todo_should_not_list_category(api, bdd_state):
    todo = bdd_state['todo_item']
    category = bdd_state['category_item']
    items = json_items(call(api, 'GET', f"/todos/{todo['id']}/categories"), 'categories')
    assert not any(str(item['id']) == str(category['id']) for item in items), items


@when('I add the todo to the category')
def add_todo_to_category(api, bdd_state):
    todo = bdd_state['todo_item']
    category = bdd_state['category_item']
    bdd_state['response'] = call(
        api, 'POST', f"/categories/{category['id']}/todos", json={'id': str(todo['id'])}
    )


@when('I add a missing todo to the category')
def add_missing_todo_to_category(api, bdd_state):
    category = bdd_state['category_item']
    bdd_state['response'] = call(
        api, 'POST', f"/categories/{category['id']}/todos", json={'id': '999999999'}
    )


@when('I remove the todo from the category')
def remove_todo_from_category(api, bdd_state):
    todo = bdd_state['todo_item']
    category = bdd_state['category_item']
    bdd_state['response'] = call(
        api, 'DELETE', f"/categories/{category['id']}/todos/{todo['id']}"
    )


@then('the category should list the todo')
def category_should_list_todo(api, bdd_state):
    todo = bdd_state['todo_item']
    category = bdd_state['category_item']
    items = json_items(call(api, 'GET', f"/categories/{category['id']}/todos"), 'todos')
    assert any(str(item['id']) == str(todo['id']) for item in items), items


@then('the category should not list the todo')
def category_should_not_list_todo(api, bdd_state):
    todo = bdd_state['todo_item']
    category = bdd_state['category_item']
    items = json_items(call(api, 'GET', f"/categories/{category['id']}/todos"), 'todos')
    assert not any(str(item['id']) == str(todo['id']) for item in items), items


@then('the todo and category should still exist')
def todo_and_category_should_still_exist(api, bdd_state):
    for entity in ('todo', 'category'):
        item = bdd_state[f'{entity}_item']
        response = call(api, 'GET', f"/{_collection(entity)}/{item['id']}")
        assert response.status_code == 200, (response.status_code, response.text)
