Feature: Delete a category
  As a user, I want to delete a category so I can remove obsolete groupings.

  Background:
    Given the Todo Manager API is available
    And the test environment is prepared

  Scenario Outline: Delete an unused category (normal flow)
    Given a category titled "<title>" exists
    When I delete the category titled "<title>"
    Then the response status should be 200
    And the category titled "<title>" should no longer exist

    Examples:
      | title             |
      | Temporary group   |
      | Old project label |

  Scenario Outline: Remove a todo assignment before deleting its category (alternate flow)
    Given a category titled "<category_title>" already contains todo "<todo_title>"
    When I remove the todo from the category
    Then the response status should be 200
    And the category should not list the todo
    When I delete the category titled "<category_title>"
    Then the response status should be 200
    And the category titled "<category_title>" should no longer exist
    And the todo titled "<todo_title>" should still be retrievable

    Examples:
      | category_title | todo_title       |
      | Old folder     | Finish cleanup   |
      | Previous term  | Return books     |

  Scenario Outline: Reject deletion of a missing category (error flow)
    When I delete a missing category with ID "<id>"
    Then the response status should be 404

    Examples:
      | id          |
      | 999999998   |
      | 999999999   |
