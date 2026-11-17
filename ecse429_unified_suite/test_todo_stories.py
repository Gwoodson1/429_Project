"""Gherkin story tests for the Todo API."""
from pytest_bdd import scenarios


scenarios('features/todos/create_todo.feature')
scenarios('features/todos/retrieve_todo.feature')
scenarios('features/todos/update_todo.feature')
scenarios('features/todos/delete_todo.feature')
scenarios('features/todos/organize_todo_categories.feature')
