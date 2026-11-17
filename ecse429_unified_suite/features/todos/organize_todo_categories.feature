Feature: Assign categories to todos
  As a user, I want to assign a category to a todo so I can organize my tasks.

  Background:
    Given the Todo Manager API is available
    And the test environment is prepared

  Scenario Outline: Assign an existing category to a todo (normal flow)
    Given a todo titled "<todo_title>" and category titled "<category_title>" exist
    When I assign the todo to the category
    Then the response status should be 201
    And the todo should list the category

    Examples:
      | todo_title       | category_title |
      | Buy supplies     | Errands        |
      | Review notes     | Study          |

  Scenario Outline: Remove a category assignment (alternate flow)
    Given a todo titled "<todo_title>" is assigned to category titled "<category_title>"
    When I remove the category from the todo
    Then the response status should be 200
    And the todo should not list the category
    And the todo and category should still exist

    Examples:
      | todo_title       | category_title |
      | Submit form      | Work           |
      | Call the clinic  | Personal       |

  Scenario Outline: Reject assignment to a missing category (error flow)
    Given a todo titled "<todo_title>" exists
    When I assign a missing category to the todo
    Then the response status should be 404

    Examples:
      | todo_title        |
      | Find a category   |
      | Plan the weekend |
