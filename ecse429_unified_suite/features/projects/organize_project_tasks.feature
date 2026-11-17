Feature: Assign tasks to projects
  As a user, I want to assign tasks to a project so I can organize project work.

  Background:
    Given the Todo Manager API is available
    And the test environment is prepared

  Scenario Outline: Assign an existing task to a project (normal flow)
    Given a project titled "<project_title>" and todo titled "<todo_title>" exist
    When I add the todo to the project
    Then the response status should be 201
    And the project should list the todo

    Examples:
      | project_title | todo_title    |
      | Release work  | Write notes   |
      | Lab work      | Run experiment |

  Scenario Outline: Remove a task from a project (alternate flow)
    Given a project titled "<project_title>" already contains todo "<todo_title>"
    When I remove the todo from the project
    Then the response status should be 200
    And the project should not list the todo
    And the project and todo should still exist

    Examples:
      | project_title | todo_title   |
      | Website       | Fix layout    |
      | Research      | Read paper   |

  Scenario Outline: Reject assigning a missing task (error flow)
    Given a project titled "<project_title>" exists
    When I add a missing todo to the project
    Then the response status should be 404

    Examples:
      | project_title |
      | Missing task  |
      | Invalid task  |
