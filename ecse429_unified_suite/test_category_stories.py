"""Gherkin story tests for the Category API."""
from pytest_bdd import scenarios


scenarios('features/categories/create_category.feature')
scenarios('features/categories/retrieve_category.feature')
scenarios('features/categories/update_category.feature')
scenarios('features/categories/delete_category.feature')
scenarios('features/categories/organize_category_todos.feature')
