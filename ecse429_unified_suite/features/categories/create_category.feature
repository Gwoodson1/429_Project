Feature: Create a category
  As a user, I want to create a category so I can organize related work.

  Background:
    Given the Todo Manager API is available
    And the test environment is prepared

  Scenario Outline: Create a category with all fields (normal flow)
    When I create a category titled "<title>" with description "<description>"
    Then the response status should be 201
    And the category titled "<title>" should exist

    Examples:
      | title         | description               |
      | School        | Coursework and study      |
      | Home          | Household responsibilities |

  Scenario Outline: Create a category with its required field only (alternate flow)
    When I create a category titled "<title>" without a description
    Then the response status should be 201
    And the category titled "<title>" should exist

    Examples:
      | title       |
      | Volunteering |
      | Travel       |

  Scenario Outline: Reject a category without a title (error flow)
    When I create a category without a title but with description "<description>"
    Then the response status should be 400

    Examples:
      | description          |
      | Missing title        |
      | Category description |
