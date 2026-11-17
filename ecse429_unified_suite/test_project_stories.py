"""Gherkin story tests for the Project API."""
from pytest_bdd import scenarios


scenarios('features/projects/create_project.feature')
scenarios('features/projects/retrieve_project.feature')
scenarios('features/projects/update_project.feature')
scenarios('features/projects/delete_project.feature')
scenarios('features/projects/organize_project_tasks.feature')
