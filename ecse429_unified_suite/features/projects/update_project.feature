Feature: Update a project
  As a user, I want to update a project so its details stay current.

  Background:
    Given the Todo Manager API is available
    And the test environment is prepared

  Scenario Outline: Update a project's description (normal flow)
    Given a project titled "<title>" exists
    When I change the project titled "<title>" description to "<description>" using POST
    Then the response status should be 200
    And the project titled "<title>" should have description "<description>"

    Examples:
      | title          | description          |
      | Sprint plan    | Updated sprint plan  |
      | Event planning | Updated event plan   |

  Scenario Outline: Replace a project with PUT (alternate flow)
    Given a project titled "<title>" exists
    When I replace the project titled "<title>" with title "<new_title>" and description "<description>" using PUT
    Then the response status should be 200
    And the project titled "<new_title>" should have description "<description>"

    Examples:
      | title        | new_title     | description       |
      | Old roadmap  | New roadmap   | Revised roadmap   |
      | Draft launch | Final launch  | Approved launch   |

  Scenario Outline: Reject replacement of a missing project (error flow)
    When I try to replace missing project ID "<item_id>"
    Then the response status should be 404

    Examples:
      | item_id   |
      | 9999971   |
      | 9999972   |
