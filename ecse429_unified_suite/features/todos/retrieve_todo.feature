Feature: Retrieve a todo
  As a user, I want to retrieve a todo so I can review its details.

  Background:
    Given the Todo Manager API is available
    And the test environment is prepared

  Scenario Outline: Retrieve an existing todo as JSON (normal flow)
    Given a todo titled "<title>" exists
    When I retrieve the todo titled "<title>" as JSON
    Then the response status should be 200
    And the todo titled "<title>" should appear in the response

    Examples:
      | title             |
      | Review schedule   |
      | Prepare meeting   |

  Scenario Outline: Retrieve an existing todo as XML (alternate flow)
    Given a todo titled "<title>" exists
    When I retrieve the todo titled "<title>" as XML
    Then the response status should be 200
    And the response should contain XML for the todo titled "<title>"

    Examples:
      | title             |
      | Check inventory   |
      | Draft proposal    |

  Scenario Outline: Reject retrieval of a missing todo (error flow)
    When I retrieve a missing todo with ID "<id>"
    Then the response status should be 404

    Examples:
      | id          |
      | 999999998   |
      | 999999999   |
