Feature: Create a project
  As a user, I want to create a project so I can organize related work.

  Background:
    Given the Todo Manager API is available
    And the test environment is prepared

  Scenario Outline: Create a project with all fields (normal flow)
    When I create a project titled "<title>" with description "<description>"
    Then the response status should be 201
    And the project titled "<title>" should exist

    Examples:
      | title           | description             |
      | Release plan    | Plan the next release   |
      | Course project  | Track project work      |

  Scenario Outline: Create a project with its required field only (alternate flow)
    When I create a project titled "<title>" without a description
    Then the response status should be 201
    And the project titled "<title>" should exist

    Examples:
      | title          |
      | Website launch |
      | Lab submission |

  Scenario Outline: Reject malformed project JSON (error flow)
    When I create a project with malformed JSON "<malformed>"
    Then the response status should be 400

    Examples:
      | malformed |
      | {bad      |
      | [broken   |
