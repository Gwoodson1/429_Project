Feature: Manage todos in a category
  As a user, I want to add and remove todos from a category so I can organize my work.

  Background:
    Given the Todo Manager API is available
    And the test environment is prepared

  Scenario Outline: Add an existing todo to a category (normal flow)
    Given a todo titled "<todo_title>" and category titled "<category_title>" exist
    When I add the todo to the category
    Then the response status should be 201
    And the category should list the todo

    Examples:
      | todo_title       | category_title |
      | Buy groceries    | Errands        |
      | Read assignment  | School         |

  Scenario Outline: Remove a todo from a category (alternate flow)
    Given a category titled "<category_title>" already contains todo "<todo_title>"
    When I remove the todo from the category
    Then the response status should be 200
    And the category should not list the todo
    And the todo and category should still exist

    Examples:
      | todo_title        | category_title |
      | Pay utility bill  | Home           |
      | Review draft      | Work           |

  Scenario Outline: Reject adding a missing todo to a category (error flow)
    Given a category titled "<category_title>" exists
    When I add a missing todo to the category
    Then the response status should be 404

    Examples:
      | category_title |
      | Study          |
      | Personal       |
