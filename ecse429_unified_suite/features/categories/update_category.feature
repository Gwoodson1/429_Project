Feature: Update a category
  As a user, I want to update a category so its information stays current.

  Background:
    Given the Todo Manager API is available
    And the test environment is prepared

  Scenario Outline: Partially update a category description (normal flow)
    Given a category titled "<title>" exists
    When I change the category titled "<title>" description to "<description>" using POST
    Then the response status should be 200
    And the category titled "<title>" should have description "<description>"

    Examples:
      | title        | description                 |
      | Work         | Current work assignments    |
      | Home         | Ongoing home projects       |

  Scenario Outline: Replace a category's details (alternate flow)
    Given a category titled "<title>" exists
    When I replace the category titled "<title>" with title "<new_title>" and description "<description>" using PUT
    Then the response status should be 200
    And the category titled "<new_title>" should have description "<description>"

    Examples:
      | title       | new_title       | description                 |
      | Old label   | New label       | Updated category details    |
      | Archive    | Completed work  | Closed projects             |

  Scenario Outline: Reject a replacement without a title (error flow)
    Given a category titled "<title>" exists
    When I try to replace the category titled "<title>" with a PUT payload missing its title
    Then the response status should be 400
    And the category titled "<title>" should have description "Initial description"

    Examples:
      | title               |
      | Retain category     |
      | Keep this grouping  |
