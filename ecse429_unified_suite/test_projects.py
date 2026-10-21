import pytest
import requests
from uuid import uuid4

BASE_URL = "http://localhost:4567"


@pytest.fixture
def new_project():
    """Create a project and clean it up after the test."""
    res = requests.post(f"{BASE_URL}/projects", json={"title": f"Fixture Project {uuid4().hex}"}, timeout=5)
    assert res.status_code == 201, res.text
    proj_id = res.json()["id"]
    yield proj_id
    requests.delete(f"{BASE_URL}/projects/{proj_id}", timeout=5)


@pytest.fixture
def new_category():
    res = requests.post(f"{BASE_URL}/categories", json={"title": f"Fixture Category {uuid4().hex}"}, timeout=5)
    assert res.status_code == 201, res.text
    cat_id = res.json()["id"]
    yield cat_id
    requests.delete(f"{BASE_URL}/categories/{cat_id}", timeout=5)


@pytest.fixture
def new_todo():
    res = requests.post(f"{BASE_URL}/todos", json={"title": f"Fixture Task {uuid4().hex}"}, timeout=5)
    assert res.status_code == 201, res.text
    todo_id = res.json()["id"]
    yield todo_id
    requests.delete(f"{BASE_URL}/todos/{todo_id}", timeout=5)


# /projects collection

def test_get_projects_json():
    res = requests.get(f"{BASE_URL}/projects", headers={"Accept": "application/json"})
    assert res.status_code == 200
    assert "application/json" in res.headers.get("Content-Type", "")


def test_get_projects_xml():
    res = requests.get(f"{BASE_URL}/projects", headers={"Accept": "application/xml"})
    assert res.status_code == 200
    assert "application/xml" in res.headers.get("Content-Type", "")


def test_head_projects():
    res = requests.head(f"{BASE_URL}/projects")
    assert res.status_code == 200
    assert not res.content


def test_options_projects():
    res = requests.options(f"{BASE_URL}/projects")
    assert res.status_code == 200


def test_post_projects_success():
    title = f"Creation Test {uuid4().hex}"
    res = requests.post(f"{BASE_URL}/projects", json={"title": title})
    assert res.status_code == 201
    proj_id = res.json()["id"]
    try:
        assert res.json()["title"] == title
    finally:
        requests.delete(f"{BASE_URL}/projects/{proj_id}")


def test_post_projects_bad_payload():
    res = requests.post(f"{BASE_URL}/projects", data="invalid json",
                        headers={"Content-Type": "application/json"})
    assert res.status_code == 400


def test_put_projects_not_allowed():
    assert requests.put(f"{BASE_URL}/projects").status_code == 405


def test_delete_projects_not_allowed():
    assert requests.delete(f"{BASE_URL}/projects").status_code == 405


def test_patch_projects_not_allowed():
    assert requests.patch(f"{BASE_URL}/projects").status_code == 405


def test_post_projects_malformed_xml():
    """Reject malformed XML on the projects collection."""
    res = requests.post(
        f"{BASE_URL}/projects",
        data="<project><title>broken</project>",
        headers={"Content-Type": "application/xml"},
    )
    assert res.status_code == 400


# /projects/:id

def test_get_specific_project_success(new_project):
    assert requests.get(f"{BASE_URL}/projects/{new_project}").status_code == 200


def test_get_specific_project_404():
    assert requests.get(f"{BASE_URL}/projects/999999").status_code == 404


def test_head_specific_project(new_project):
    assert requests.head(f"{BASE_URL}/projects/{new_project}").status_code == 200


def test_options_specific_project(new_project):
    assert requests.options(f"{BASE_URL}/projects/{new_project}").status_code == 200


def test_post_specific_project_amend(new_project):
    res = requests.post(f"{BASE_URL}/projects/{new_project}", json={"title": "Amended via POST"})
    assert res.status_code == 200
    assert res.json()["title"] == "Amended via POST"


def test_put_specific_project_amend(new_project):
    res = requests.put(f"{BASE_URL}/projects/{new_project}", json={"title": "Amended via PUT"})
    assert res.status_code == 200


def test_delete_specific_project(new_project):
    res = requests.delete(f"{BASE_URL}/projects/{new_project}")
    assert res.status_code == 200
    assert requests.get(f"{BASE_URL}/projects/{new_project}").status_code == 404


# /projects/:id/tasks

def test_get_project_tasks(new_project):
    assert requests.get(f"{BASE_URL}/projects/{new_project}/tasks").status_code == 200


def test_post_project_task_relationship(new_project, new_todo):
    res = requests.post(f"{BASE_URL}/projects/{new_project}/tasks", json={"id": str(new_todo)})
    assert res.status_code == 201


def test_post_project_task_relationship_404(new_project):
    res = requests.post(f"{BASE_URL}/projects/{new_project}/tasks", json={"id": "99999"})
    assert res.status_code == 404


def test_head_project_tasks(new_project):
    assert requests.head(f"{BASE_URL}/projects/{new_project}/tasks").status_code == 200


def test_options_project_tasks(new_project):
    assert requests.options(f"{BASE_URL}/projects/{new_project}/tasks").status_code == 200


def test_delete_project_task_relationship(new_project, new_todo):
    created = requests.post(f"{BASE_URL}/projects/{new_project}/tasks", json={"id": str(new_todo)})
    assert created.status_code == 201
    res = requests.delete(f"{BASE_URL}/projects/{new_project}/tasks/{new_todo}")
    assert res.status_code == 200


def test_delete_project_task_relationship_404(new_project):
    assert requests.delete(f"{BASE_URL}/projects/{new_project}/tasks/99999").status_code == 404


# /projects/:id/categories

def test_get_project_categories(new_project):
    assert requests.get(f"{BASE_URL}/projects/{new_project}/categories").status_code == 200


def test_post_project_category_relationship(new_project, new_category):
    res = requests.post(f"{BASE_URL}/projects/{new_project}/categories", json={"id": str(new_category)})
    assert res.status_code == 201


def test_head_project_categories(new_project):
    assert requests.head(f"{BASE_URL}/projects/{new_project}/categories").status_code == 200


def test_options_project_categories(new_project):
    assert requests.options(f"{BASE_URL}/projects/{new_project}/categories").status_code == 200


def test_delete_project_category_relationship(new_project, new_category):
    created = requests.post(f"{BASE_URL}/projects/{new_project}/categories", json={"id": str(new_category)})
    assert created.status_code == 201
    res = requests.delete(f"{BASE_URL}/projects/{new_project}/categories/{new_category}")
    assert res.status_code == 200


# /docs

def test_get_docs():
    res = requests.get(f"{BASE_URL}/docs")
    assert res.status_code == 200
    assert "text/html" in res.headers.get("Content-Type", "")


def test_options_docs():
    res = requests.options(f"{BASE_URL}/docs")
    assert res.status_code in (200, 404)
