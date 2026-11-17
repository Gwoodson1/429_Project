Feature: Retrieve a project
  As a user, I want to retrieve a project so I can review its details.

  Background:
    Given the Todo Manager API is available
    And the test environment is prepared

  Scenario Outline: Retrieve a project as JSON (normal flow)
    Given a project titled "<title>" exists
    When I retrieve the project titled "<title>" as JSON
    Then the response status should be 200
    And the project titled "<title>" should appear in the response

    Examples:
      | title          |
      | Mobile release |
      | Exam schedule  |

  Scenario Outline: Retrieve a project as XML (alternate flow)
    Given a project titled "<title>" exists
    When I retrieve the project titled "<title>" as XML
    Then the response status should be 200
    And the response should contain XML for the project titled "<title>"

    Examples:
      | title          |
      | Client work    |
      | Research plan  |

  Scenario Outline: Reject retrieval of a missing project (error flow)
    When I retrieve a missing project with ID "<item_id>"
    Then the response status should be 404

    Examples:
      | item_id |
      | 9999991 |
      | 9999992 |
