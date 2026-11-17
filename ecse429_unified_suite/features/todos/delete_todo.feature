Feature: Delete a todo
  As a user, I want to delete a todo so I can remove tasks I no longer need.

  Background:
    Given the Todo Manager API is available
    And the test environment is prepared

  Scenario Outline: Delete an active todo (normal flow)
    Given a todo titled "<title>" exists
    When I delete the todo titled "<title>"
    Then the response status should be 200
    And the todo titled "<title>" should no longer exist

    Examples:
      | title              |
      | Remove old draft   |
      | Cancel reminder    |

  Scenario Outline: Delete a completed todo (alternate flow)
    Given a completed todo titled "<title>" exists
    When I delete the todo titled "<title>"
    Then the response status should be 200
    And the todo titled "<title>" should no longer exist

    Examples:
      | title              |
      | Archive finished   |
      | Close resolved     |

  Scenario Outline: Reject deletion of a missing todo (error flow)
    When I delete a missing todo with ID "<id>"
    Then the response status should be 404

    Examples:
      | id          |
      | 999999998   |
      | 999999999   |
