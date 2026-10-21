"""Todos API tests. Run with: python -m pytest -v test_todos.py"""

import pytest
from conftest import call, json_items, xml_root


def new_todo(resources, unique_title):
    return resources('todos', title=unique_title, description='Initial description', doneStatus=False)


def new_category(resources, unique_title):
    return resources('categories', title=unique_title, description='Test category')


def new_project(resources, unique_title):
    return resources('projects', title=unique_title, description='Test project')


class TestTodoCollection:
    def test_list_json(self, api):
        assert isinstance(json_items(call(api, 'GET', '/todos'), 'todos'), list)

    def test_list_xml(self, api):
        root = xml_root(call(api, 'GET', '/todos', headers={'Accept': 'application/xml'}))
        assert root.tag == 'todos'

    def test_create_and_retrieve(self, api, resources, unique_title):
        todo = new_todo(resources, unique_title)
        matches = json_items(call(api, 'GET', f"/todos/{todo['id']}"), 'todos')
        assert len(matches) == 1
        assert matches[0]['title'] == unique_title
        assert matches[0]['description'] == 'Initial description'

    def test_create_with_xml(self, api, resources, unique_title):
        # This tests XML input as well as XML output; created item is registered for cleanup.
        import xml.sax.saxutils as sx
        xml = f'<todo><title>{sx.escape(unique_title)}</title><description>XML creation</description><doneStatus>false</doneStatus></todo>'
        response = call(api, 'POST', '/todos', data=xml.encode(), headers={'Content-Type': 'application/xml', 'Accept': 'application/json'})
        assert response.status_code == 201, response.text
        item_id = response.json()['id']
        # Explicit cleanup because this request did not use the resource factory.
        try:
            matches = json_items(call(api, 'GET', f'/todos/{item_id}'), 'todos')
            assert matches[0]['title'] == unique_title
        finally:
            call(api, 'DELETE', f'/todos/{item_id}')

    @pytest.mark.parametrize('method', ['PUT', 'DELETE', 'PATCH'])
    def test_disallowed_collection_methods(self, api, method):
        assert call(api, method, '/todos').status_code == 405

    def test_collection_head(self, api):
        assert call(api, 'HEAD', '/todos').status_code == 200

    def test_collection_options(self, api):
        assert call(api, 'OPTIONS', '/todos').status_code == 200

    @pytest.mark.parametrize('payload,content_type', [
        ('{"title":', 'application/json'),
        ('<todo><title>broken</todo>', 'application/xml'),
    ])
    def test_malformed_create(self, api, payload, content_type):
        response = call(api, 'POST', '/todos', data=payload, headers={'Content-Type': content_type})
        assert response.status_code == 400, response.text

    def test_missing_title_rejected(self, api):
        response = call(api, 'POST', '/todos', json={'description': 'No title'})
        assert response.status_code == 400, response.text


class TestTodoItem:
    def test_get_xml(self, api, resources, unique_title):
        todo = new_todo(resources, unique_title)
        root = xml_root(call(api, 'GET', f"/todos/{todo['id']}", headers={'Accept': 'application/xml'}))
        assert root.tag == 'todos'
        assert any(el.text == unique_title for el in root.iter('title'))

    def test_update_with_post_partial(self, api, resources, unique_title):
        todo = new_todo(resources, unique_title)
        response = call(api, 'POST', f"/todos/{todo['id']}", json={'description': 'Changed by POST'})
        assert response.status_code == 200, response.text
        found = json_items(call(api, 'GET', f"/todos/{todo['id']}"), 'todos')[0]
        assert found['description'] == 'Changed by POST'
        assert found['title'] == unique_title

    def test_update_with_put_complete(self, api, resources, unique_title):
        todo = new_todo(resources, unique_title)
        response = call(api, 'PUT', f"/todos/{todo['id']}", json={
            'title': unique_title + ' updated', 'description': 'Changed by PUT', 'doneStatus': True
        })
        assert response.status_code == 200, response.text
        found = json_items(call(api, 'GET', f"/todos/{todo['id']}"), 'todos')[0]
        assert found['title'] == unique_title + ' updated'
        assert found['description'] == 'Changed by PUT'
        assert str(found['doneStatus']).lower() == 'true'

    def test_put_without_title_rejected_and_unchanged(self, api, resources, unique_title):
        todo = new_todo(resources, unique_title)
        response = call(api, 'PUT', f"/todos/{todo['id']}", json={'description': 'Should not apply'})
        assert response.status_code == 400, response.text
        found = json_items(call(api, 'GET', f"/todos/{todo['id']}"), 'todos')[0]
        assert found['title'] == unique_title
        assert found['description'] == 'Initial description'

    def test_delete_then_get_and_delete_again(self, api, resources, unique_title):
        todo = new_todo(resources, unique_title)
        path = f"/todos/{todo['id']}"
        assert call(api, 'DELETE', path).status_code == 200
        assert call(api, 'GET', path).status_code == 404
        assert call(api, 'DELETE', path).status_code == 404

    @pytest.mark.parametrize('method', ['GET', 'POST', 'PUT', 'DELETE', 'HEAD'])
    def test_missing_item(self, api, method):
        kwargs = {'json': {'title': 'Missing item'}} if method in ('POST', 'PUT') else {}
        assert call(api, method, '/todos/999999999', **kwargs).status_code == 404

    def test_item_head_options_patch(self, api, resources, unique_title):
        todo = new_todo(resources, unique_title)
        path = f"/todos/{todo['id']}"
        assert call(api, 'HEAD', path).status_code == 200
        assert call(api, 'OPTIONS', path).status_code == 200
        assert call(api, 'PATCH', path).status_code == 405


@pytest.mark.parametrize('relation,target_kind,collection', [
    ('categories', 'categories', 'categories'),
    ('tasksof', 'projects', 'projects'),
])
class TestTodoRelationships:
    def test_create_read_remove_link(self, api, resources, unique_title, relation, target_kind, collection):
        todo = new_todo(resources, unique_title)
        target = resources(target_kind, title=unique_title + ' related', description='Linked')
        base = f"/todos/{todo['id']}/{relation}"
        assert json_items(call(api, 'GET', base), collection) == []
        response = call(api, 'POST', base, json={'id': target['id']})
        assert response.status_code == 201, response.text
        linked = json_items(call(api, 'GET', base), collection)
        assert any(str(item['id']) == str(target['id']) for item in linked)
        link_path = f"{base}/{target['id']}"
        assert call(api, 'DELETE', link_path).status_code == 200
        assert not any(str(item['id']) == str(target['id']) for item in json_items(call(api, 'GET', base), collection))
        assert call(api, 'DELETE', link_path).status_code in (400, 404)
        # Removing the relationship must not delete either object.
        assert call(api, 'GET', f"/todos/{todo['id']}").status_code == 200
        assert call(api, 'GET', f"/{target_kind}/{target['id']}").status_code == 200

    def test_relationship_collection_methods(self, api, resources, unique_title, relation, target_kind, collection):
        todo = new_todo(resources, unique_title)
        base = f"/todos/{todo['id']}/{relation}"
        assert call(api, 'HEAD', base).status_code == 200
        assert call(api, 'OPTIONS', base).status_code == 200
        for method in ('PUT', 'DELETE', 'PATCH'):
            assert call(api, method, base).status_code == 405

    def test_individual_link_disallowed_methods(self, api, resources, unique_title, relation, target_kind, collection):
        todo = new_todo(resources, unique_title)
        target = resources(target_kind, title=unique_title + ' linked')
        base = f"/todos/{todo['id']}/{relation}"
        assert call(api, 'POST', base, json={'id': target['id']}).status_code == 201
        path = f"{base}/{target['id']}"
        assert call(api, 'OPTIONS', path).status_code == 200
        for method in ('PUT', 'PATCH'):
            assert call(api, method, path).status_code == 405

    @pytest.mark.parametrize('method', ['GET', 'POST', 'HEAD'])
    @pytest.mark.xfail(strict=True, reason='Known documentation mismatch: API returns 404 instead of documented 405')
    def test_documented_individual_link_status(self, api, resources, unique_title, relation, target_kind, collection, method):
        """EXPECTED documented behavior; intentionally xfails until API conforms."""
        todo = new_todo(resources, unique_title)
        target = resources(target_kind, title=unique_title + ' linked')
        base = f"/todos/{todo['id']}/{relation}"
        assert call(api, 'POST', base, json={'id': target['id']}).status_code == 201
        assert call(api, method, f"{base}/{target['id']}").status_code == 405

    @pytest.mark.parametrize('method', ['GET', 'POST', 'HEAD'])
    def test_actual_individual_link_status(self, api, resources, unique_title, relation, target_kind, collection, method):
        """ACTUAL observed behavior, separately verified from documented expectation."""
        todo = new_todo(resources, unique_title)
        target = resources(target_kind, title=unique_title + ' linked')
        base = f"/todos/{todo['id']}/{relation}"
        assert call(api, 'POST', base, json={'id': target['id']}).status_code == 201
        assert call(api, method, f"{base}/{target['id']}").status_code == 404
