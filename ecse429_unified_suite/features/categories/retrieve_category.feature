Feature: Retrieve a category
  As a user, I want to retrieve a category so I can review its details.

  Background:
    Given the Todo Manager API is available
    And the test environment is prepared

  Scenario Outline: Retrieve an existing category as JSON (normal flow)
    Given a category titled "<title>" exists
    When I retrieve the category titled "<title>" as JSON
    Then the response status should be 200
    And the category titled "<title>" should appear in the response

    Examples:
      | title        |
      | Work         |
      | Household    |

  Scenario Outline: Retrieve an existing category as XML (alternate flow)
    Given a category titled "<title>" exists
    When I retrieve the category titled "<title>" as XML
    Then the response status should be 200
    And the response should contain XML for the category titled "<title>"

    Examples:
      | title        |
      | Recreation   |
      | Learning     |

  Scenario Outline: Reject retrieval of a missing category (error flow)
    When I retrieve a missing category with ID "<id>"
    Then the response status should be 404

    Examples:
      | id          |
      | 999999998   |
      | 999999999   |
