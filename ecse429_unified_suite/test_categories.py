"""Categories API tests. Run with: python -m pytest -v test_categories.py"""

import pytest
from conftest import call, json_items, xml_root


def new_category(resources, unique_title):
    return resources('categories', title=unique_title, description='Initial description')


class TestCategoryCollection:
    def test_list_json(self, api):
        assert isinstance(json_items(call(api, 'GET', '/categories'), 'categories'), list)

    def test_list_xml(self, api):
        assert xml_root(call(api, 'GET', '/categories', headers={'Accept': 'application/xml'})).tag == 'categories'

    def test_create_and_retrieve(self, api, resources, unique_title):
        category = new_category(resources, unique_title)
        items = json_items(call(api, 'GET', f"/categories/{category['id']}"), 'categories')
        assert len(items) == 1
        assert items[0]['title'] == unique_title
        assert items[0]['description'] == 'Initial description'

    def test_create_with_xml(self, api, unique_title):
        import xml.sax.saxutils as sx
        xml = f'<category><title>{sx.escape(unique_title)}</title><description>XML creation</description></category>'
        response = call(api, 'POST', '/categories', data=xml.encode(), headers={'Content-Type': 'application/xml', 'Accept': 'application/json'})
        assert response.status_code == 201, response.text
        item_id = response.json()['id']
        try:
            items = json_items(call(api, 'GET', f'/categories/{item_id}'), 'categories')
            assert items[0]['title'] == unique_title
        finally:
            call(api, 'DELETE', f'/categories/{item_id}')

    @pytest.mark.parametrize('method', ['PUT', 'DELETE', 'PATCH'])
    def test_disallowed_collection_methods(self, api, method):
        assert call(api, method, '/categories').status_code == 405

    def test_collection_head_and_options(self, api):
        assert call(api, 'HEAD', '/categories').status_code == 200
        assert call(api, 'OPTIONS', '/categories').status_code == 200

    @pytest.mark.parametrize('payload,content_type', [
        ('{"title":', 'application/json'),
        ('<category><title>broken</category>', 'application/xml'),
    ])
    def test_malformed_create(self, api, payload, content_type):
        assert call(api, 'POST', '/categories', data=payload, headers={'Content-Type': content_type}).status_code == 400

    def test_missing_title_rejected(self, api):
        assert call(api, 'POST', '/categories', json={'description': 'No title'}).status_code == 400


class TestCategoryItem:
    def test_get_xml(self, api, resources, unique_title):
        category = new_category(resources, unique_title)
        root = xml_root(call(api, 'GET', f"/categories/{category['id']}", headers={'Accept': 'application/xml'}))
        assert root.tag == 'categories'
        assert any(el.text == unique_title for el in root.iter('title'))

    def test_post_partial_update(self, api, resources, unique_title):
        category = new_category(resources, unique_title)
        path = f"/categories/{category['id']}"
        assert call(api, 'POST', path, json={'description': 'Updated via POST'}).status_code == 200
        found = json_items(call(api, 'GET', path), 'categories')[0]
        assert found['description'] == 'Updated via POST'
        assert found['title'] == unique_title

    def test_put_complete_update(self, api, resources, unique_title):
        category = new_category(resources, unique_title)
        path = f"/categories/{category['id']}"
        response = call(api, 'PUT', path, json={'title': unique_title + ' updated', 'description': 'Updated via PUT'})
        assert response.status_code == 200, response.text
        found = json_items(call(api, 'GET', path), 'categories')[0]
        assert found['title'] == unique_title + ' updated'
        assert found['description'] == 'Updated via PUT'

    def test_put_without_title_rejected_and_unchanged(self, api, resources, unique_title):
        category = new_category(resources, unique_title)
        path = f"/categories/{category['id']}"
        assert call(api, 'PUT', path, json={'description': 'Should not apply'}).status_code == 400
        found = json_items(call(api, 'GET', path), 'categories')[0]
        assert found['title'] == unique_title
        assert found['description'] == 'Initial description'

    def test_delete_then_get_and_delete_again(self, api, resources, unique_title):
        category = new_category(resources, unique_title)
        path = f"/categories/{category['id']}"
        assert call(api, 'DELETE', path).status_code == 200
        assert call(api, 'GET', path).status_code == 404
        assert call(api, 'DELETE', path).status_code == 404

    @pytest.mark.parametrize('method', ['GET', 'POST', 'PUT', 'DELETE', 'HEAD'])
    def test_missing_item(self, api, method):
        kwargs = {'json': {'title': 'Missing item'}} if method in ('POST', 'PUT') else {}
        assert call(api, method, '/categories/999999999', **kwargs).status_code == 404

    def test_item_head_options_patch(self, api, resources, unique_title):
        category = new_category(resources, unique_title)
        path = f"/categories/{category['id']}"
        assert call(api, 'HEAD', path).status_code == 200
        assert call(api, 'OPTIONS', path).status_code == 200
        assert call(api, 'PATCH', path).status_code == 405


@pytest.mark.parametrize('relation,target_kind,collection', [
    ('todos', 'todos', 'todos'),
    ('projects', 'projects', 'projects'),
])
class TestCategoryRelationships:
    def test_create_read_remove_link(self, api, resources, unique_title, relation, target_kind, collection):
        category = new_category(resources, unique_title)
        fields = {'title': unique_title + ' linked'}
        if target_kind == 'todos':
            fields['doneStatus'] = False
        target = resources(target_kind, **fields)
        base = f"/categories/{category['id']}/{relation}"
        assert json_items(call(api, 'GET', base), collection) == []
        response = call(api, 'POST', base, json={'id': target['id']})
        assert response.status_code == 201, response.text
        assert any(str(x['id']) == str(target['id']) for x in json_items(call(api, 'GET', base), collection))
        link_path = f"{base}/{target['id']}"
        assert call(api, 'DELETE', link_path).status_code == 200
        assert not any(str(x['id']) == str(target['id']) for x in json_items(call(api, 'GET', base), collection))
        assert call(api, 'DELETE', link_path).status_code in (400, 404)
        assert call(api, 'GET', f"/categories/{category['id']}").status_code == 200
        assert call(api, 'GET', f"/{target_kind}/{target['id']}").status_code == 200

    def test_relationship_collection_methods(self, api, resources, unique_title, relation, target_kind, collection):
        category = new_category(resources, unique_title)
        base = f"/categories/{category['id']}/{relation}"
        assert call(api, 'HEAD', base).status_code == 200
        assert call(api, 'OPTIONS', base).status_code == 200
        for method in ('PUT', 'DELETE', 'PATCH'):
            assert call(api, method, base).status_code == 405

    def test_individual_link_disallowed_methods(self, api, resources, unique_title, relation, target_kind, collection):
        category = new_category(resources, unique_title)
        target = resources(target_kind, title=unique_title + ' linked')
        base = f"/categories/{category['id']}/{relation}"
        assert call(api, 'POST', base, json={'id': target['id']}).status_code == 201
        path = f"{base}/{target['id']}"
        assert call(api, 'OPTIONS', path).status_code == 200
        for method in ('PUT', 'PATCH'):
            assert call(api, method, path).status_code == 405

    @pytest.mark.parametrize('method', ['GET', 'POST', 'HEAD'])
    @pytest.mark.xfail(strict=True, reason='Known documentation mismatch: API returns 404 instead of documented 405')
    def test_documented_individual_link_status(self, api, resources, unique_title, relation, target_kind, collection, method):
        """EXPECTED documented behavior; intentionally xfails until API conforms."""
        category = new_category(resources, unique_title)
        target = resources(target_kind, title=unique_title + ' linked')
        base = f"/categories/{category['id']}/{relation}"
        assert call(api, 'POST', base, json={'id': target['id']}).status_code == 201
        assert call(api, method, f"{base}/{target['id']}").status_code == 405

    @pytest.mark.parametrize('method', ['GET', 'POST', 'HEAD'])
    def test_actual_individual_link_status(self, api, resources, unique_title, relation, target_kind, collection, method):
        """ACTUAL observed behavior; separate from the documented-expectation test."""
        category = new_category(resources, unique_title)
        target = resources(target_kind, title=unique_title + ' linked')
        base = f"/categories/{category['id']}/{relation}"
        assert call(api, 'POST', base, json={'id': target['id']}).status_code == 201
        assert call(api, method, f"{base}/{target['id']}").status_code == 404
