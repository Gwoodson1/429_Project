import pytest
import requests
from requests.exceptions import ConnectionError

BASE_URL = "http://localhost:4567"

# --- FIXTURES FOR STATELESS TESTING ---
@pytest.fixture
def new_project():
    """Creates a project before a test and deletes it after."""
    res = requests.post(f"{BASE_URL}/projects", json={"title": "Fixture Project"})
    proj_id = res.json().get("id")
    yield proj_id
    requests.delete(f"{BASE_URL}/projects/{proj_id}")

@pytest.fixture
def new_category():
    """Creates a category for relationship testing."""
    res = requests.post(f"{BASE_URL}/categories", json={"title": "Fixture Category"})
    cat_id = res.json().get("id")
    yield cat_id
    requests.delete(f"{BASE_URL}/categories/{cat_id}")

@pytest.fixture
def new_todo():
    """Creates a todo (task) for relationship testing."""
    res = requests.post(f"{BASE_URL}/todos", json={"title": "Fixture Task"})
    todo_id = res.json().get("id")
    yield todo_id
    requests.delete(f"{BASE_URL}/todos/{todo_id}")


# --- /projects ENDPOINT TESTS ---

def test_get_projects_json():
    # Return all instances of project[cite: 1]
    res = requests.get(f"{BASE_URL}/projects", headers={"Accept": "application/json"})
    assert res.status_code == 200
    assert "application/json" in res.headers.get("Content-Type", "")

def test_get_projects_xml():
    # Application supports XML via headers
    res = requests.get(f"{BASE_URL}/projects", headers={"Accept": "application/xml"})
    assert res.status_code == 200
    assert "application/xml" in res.headers.get("Content-Type", "")

def test_head_projects():
    # Headers for all instances of project[cite: 1]
    res = requests.head(f"{BASE_URL}/projects")
    assert res.status_code == 200
    assert not res.text # HEAD should have no body

def test_options_projects():
    # Show all Options for endpoint[cite: 1]
    res = requests.options(f"{BASE_URL}/projects")
    assert res.status_code == 200

def test_post_projects_success():
    # Create project without ID[cite: 1]
    res = requests.post(f"{BASE_URL}/projects", json={"title": "Creation Test"})
    assert res.status_code == 201
    assert res.json()["title"] == "Creation Test"

def test_post_projects_bad_payload():
    # Error when creating a project[cite: 1]
    res = requests.post(f"{BASE_URL}/projects", data="invalid json")
    assert res.status_code == 400

def test_put_projects_not_allowed():
    # Method not allowed[cite: 1]
    res = requests.put(f"{BASE_URL}/projects")
    assert res.status_code == 405

def test_delete_projects_not_allowed():
    # Method not allowed[cite: 1]
    res = requests.delete(f"{BASE_URL}/projects")
    assert res.status_code == 405

def test_patch_projects_not_allowed():
    # Method not allowed[cite: 1]
    res = requests.patch(f"{BASE_URL}/projects")
    assert res.status_code == 405


# --- /projects/:id ENDPOINT TESTS ---

def test_get_specific_project_success(new_project):
    # Return a specific instances of project[cite: 1]
    res = requests.get(f"{BASE_URL}/projects/{new_project}")
    assert res.status_code == 200

def test_get_specific_project_404():
    # Could not find a specific project[cite: 1]
    res = requests.get(f"{BASE_URL}/projects/999999")
    assert res.status_code == 404

def test_head_specific_project(new_project):
    # Headers for a specific instance[cite: 1]
    res = requests.head(f"{BASE_URL}/projects/{new_project}")
    assert res.status_code == 200

def test_options_specific_project(new_project):
    # Show all Options for endpoint of projects/:id[cite: 1]
    res = requests.options(f"{BASE_URL}/projects/{new_project}")
    assert res.status_code == 200

def test_post_specific_project_amend(new_project):
    # Amend a specific instances of project[cite: 1]
    res = requests.post(f"{BASE_URL}/projects/{new_project}", json={"title": "Amended via POST"})
    assert res.status_code == 200
    assert res.json()["title"] == "Amended via POST"

def test_put_specific_project_amend(new_project):
    # Amend a specific instances using PUT[cite: 1]
    res = requests.put(f"{BASE_URL}/projects/{new_project}", json={"title": "Amended via PUT"})
    assert res.status_code == 200

def test_delete_specific_project(new_project):
    # Delete a specific instances of project[cite: 1]
    res = requests.delete(f"{BASE_URL}/projects/{new_project}")
    assert res.status_code == 200
    
    # Verify deletion
    check = requests.get(f"{BASE_URL}/projects/{new_project}")
    assert check.status_code == 404


# --- /projects/:id/tasks RELATIONSHIP TESTS ---

def test_get_project_tasks(new_project):
    # Return all todo items related to project[cite: 1]
    res = requests.get(f"{BASE_URL}/projects/{new_project}/tasks")
    assert res.status_code == 200

def test_post_project_task_relationship(new_project, new_todo):
    # Create relationship between project and todo[cite: 1]
    res = requests.post(f"{BASE_URL}/projects/{new_project}/tasks", json={"id": str(new_todo)})
    assert res.status_code == 201

def test_post_project_task_relationship_404(new_project):
    # Error when creating relationship with non-existent task
    res = requests.post(f"{BASE_URL}/projects/{new_project}/tasks", json={"id": "99999"})
    assert res.status_code == 404

def test_head_project_tasks(new_project):
    # Headers for todo items related to project[cite: 1]
    res = requests.head(f"{BASE_URL}/projects/{new_project}/tasks")
    assert res.status_code == 200

def test_options_project_tasks(new_project):
    # Show all Options for endpoint[cite: 1]
    res = requests.options(f"{BASE_URL}/projects/{new_project}/tasks")
    assert res.status_code == 200

def test_delete_project_task_relationship(new_project, new_todo):
    # Delete instance of relationship[cite: 1]
    requests.post(f"{BASE_URL}/projects/{new_project}/tasks", json={"id": str(new_todo)})
    res = requests.delete(f"{BASE_URL}/projects/{new_project}/tasks/{new_todo}")
    assert res.status_code == 200

def test_delete_project_task_relationship_404(new_project):
    # Relationship not found[cite: 1]
    res = requests.delete(f"{BASE_URL}/projects/{new_project}/tasks/99999")
    assert res.status_code == 404


# --- /projects/:id/categories RELATIONSHIP TESTS ---

def test_get_project_categories(new_project):
    # Return all category items related to project[cite: 1]
    res = requests.get(f"{BASE_URL}/projects/{new_project}/categories")
    assert res.status_code == 200

def test_post_project_category_relationship(new_project, new_category):
    # Create relationship between project and category[cite: 1]
    res = requests.post(f"{BASE_URL}/projects/{new_project}/categories", json={"id": str(new_category)})
    assert res.status_code == 201

def test_head_project_categories(new_project):
    # Headers for category items related to project[cite: 1]
    res = requests.head(f"{BASE_URL}/projects/{new_project}/categories")
    assert res.status_code == 200

def test_options_project_categories(new_project):
    # Show all Options for endpoint[cite: 1]
    res = requests.options(f"{BASE_URL}/projects/{new_project}/categories")
    assert res.status_code == 200

def test_delete_project_category_relationship(new_project, new_category):
    # Delete instance of relationship[cite: 1]
    requests.post(f"{BASE_URL}/projects/{new_project}/categories", json={"id": str(new_category)})
    res = requests.delete(f"{BASE_URL}/projects/{new_project}/categories/{new_category}")
    assert res.status_code == 200


# --- /docs ENDPOINT TESTS ---

def test_get_docs():
    # Test undocumented /docs discovery
    res = requests.get(f"{BASE_URL}/docs")
    assert res.status_code == 200
    assert "text/html" in res.headers.get("Content-Type", "")

def test_options_docs():
    res = requests.options(f"{BASE_URL}/docs")
    assert res.status_code in [200, 404] # Undocumented, verifying server handling
