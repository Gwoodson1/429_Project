# ECSE 429 unified API test suite

Tests for Todos, Categories, and Projects using Python, pytest, and requests.

## Running
Start the Todo Manager REST API on http://localhost:4567 in a separate terminal.

From this folder in PowerShell:
```
py -m pip install -r requirements.txt
py -m pip install pytest-randomly
py -m pytest -v test_todos.py test_categories.py test_projects.py
py -m pytest -v --randomly-seed=12345 test_todos.py test_categories.py test_projects.py
py -m pytest -v -ra test_todos.py test_categories.py test_projects.py 2>&1 | Tee-Object -FilePath pytest-results.txt
```

Expected collection: 112 tests (41 Todos, 40 Categories, 31 Projects).
Prior individual runs yielded 100 passed and 12 XFAIL, but the three-module combined run has NOT been verified against your local server.

## Notes
- Projects tests were integrated from the teammate's submitted source with minor hygiene improvements: unique fixture titles, deletion of a project created in the collection test, and explicit JSON Content-Type for malformed input.
- Project tests retain their original assertions, including the permissive /docs OPTIONS status assertion.
- Todos/Categories expected-failure tests intentionally expose documentation-versus-implementation differences.
- Review the project's prohibition on automatically generated unit test code before submission.
