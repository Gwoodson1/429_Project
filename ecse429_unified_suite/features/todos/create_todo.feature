Feature: Create a todo
  As a user, I want to create a todo so I can track a task.

  Background:
    Given the Todo Manager API is available
    And the test environment is prepared

  Scenario Outline: Create a todo with all fields (normal flow)
    When I create a todo titled "<title>" with description "<description>"
    Then the response status should be 201
    And the todo titled "<title>" should exist

    Examples:
      | title           | description          |
      | Finish report   | Complete the report  |
      | Review lecture  | Study chapter 4      |

  Scenario Outline: Create a todo with its required field only (alternate flow)
    When I create a todo titled "<title>" without a description
    Then the response status should be 201
    And the todo titled "<title>" should exist

    Examples:
      | title           |
      | Call the office |
      | Pay the bill    |

  Scenario Outline: Reject a todo without a title (error flow)
    When I create a todo without a title but with description "<description>"
    Then the response status should be 400

    Examples:
      | description         |
      | Missing title       |
      | Description only    |
