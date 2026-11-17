Feature: Update a todo
  As a user, I want to update a todo so I can keep its details current.

  Background:
    Given the Todo Manager API is available
    And the test environment is prepared

  Scenario Outline: Partially update a todo description (normal flow)
    Given a todo titled "<title>" exists
    When I change the todo titled "<title>" description to "<description>" using POST
    Then the response status should be 200
    And the todo titled "<title>" should have description "<description>"

    Examples:
      | title             | description          |
      | Update agenda     | Agenda is finalized  |
      | Submit timesheet  | Hours are recorded   |

  Scenario Outline: Replace a todo and mark it complete (alternate flow)
    Given a todo titled "<title>" exists
    When I replace the todo titled "<title>" with title "<new_title>" and description "<description>" using PUT
    Then the response status should be 200
    And the todo titled "<new_title>" should have description "<description>"
    And the todo titled "<new_title>" should be marked complete

    Examples:
      | title           | new_title           | description           |
      | Read chapter    | Read chapter done   | Chapter 4 completed   |
      | Send invoice    | Invoice sent        | Invoice was sent      |

  Scenario Outline: Reject a replacement without a title (error flow)
    Given a todo titled "<title>" exists
    When I try to replace the todo titled "<title>" with a PUT payload missing its title
    Then the response status should be 400
    And the todo titled "<title>" should have description "Initial description"

    Examples:
      | title             |
      | Keep this todo    |
      | Preserve this one |
