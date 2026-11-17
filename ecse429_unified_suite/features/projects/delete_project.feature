Feature: Delete a project
  As a user, I want to delete a project so obsolete work is removed.

  Background:
    Given the Todo Manager API is available
    And the test environment is prepared

  Scenario Outline: Delete an existing project (normal flow)
    Given a project titled "<title>" exists
    When I delete the project titled "<title>"
    Then the response status should be 200
    And the project titled "<title>" should no longer exist

    Examples:
      | title          |
      | Completed work |
      | Archived plan  |

  Scenario Outline: Keep another project available after deletion (alternate flow)
    Given a project titled "<title>" exists
    When I delete the project titled "<title>"
    Then the response status should be 200
    And the project titled "<title>" should no longer exist

    Examples:
      | title          |
      | Closed sprint  |
      | Old assignment |

  Scenario Outline: Reject deletion of a missing project (error flow)
    When I delete a missing project with ID "<item_id>"
    Then the response status should be 404

    Examples:
      | item_id |
      | 9999981 |
      | 9999982 |
