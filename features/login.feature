Feature: Login Functionality


  @smoke @login
  Scenario Outline: Successful login with valid users

    Given user launches the application
    When user logs in with username "<username>" and password "<password>"
    Then the user should be redirected to the inventory page

    Examples:
      | username                | password     |
      | standard_user           | secret_sauce |
      | problem_user            | secret_sauce |
      | performance_glitch_user | secret_sauce |
      | bharadwaj               | bharadwaj    |


  @negative @login
  Scenario Outline: Unsuccessful login with invalid credentials

    Given user launches the application
    When user logs in with username "<username>" and password "<password>"
    Then the user should see the error message "<error_message>"

    Examples:
      | username      | password     | error_message                                                             |
      | invalid_user  | secret_sauce | Epic sadface: Username and password do not match any user in this service |
      | standard_user | wrong_pass   | Epic sadface: Username and password do not match any user in this service |


  @negative @login
  Scenario Outline: Login with empty username

    Given user launches the application
    When user logs in with empty username and password "<password>"
    Then the user should see the error message "<error_message>"

    Examples:
      | password     | error_message                       |
      | secret_sauce | Epic sadface: Username is required |


  @negative @login
  Scenario Outline: Login with empty password

    Given user launches the application
    When user logs in with username "<username>" and empty password
    Then the user should see the error message "<error_message>"

    Examples:
      | username      | error_message                       |
      | standard_user | Epic sadface: Password is required |


  @negative @login
  Scenario: Login with a locked account

    Given user launches the application
    When user logs in with username "locked_out_user" and password "secret_sauce"
    Then the user should see the error message "Epic sadface: Sorry, this user has been locked out."