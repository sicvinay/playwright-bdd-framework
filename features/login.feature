Feature: Login Functionality

  Scenario: Successful Login

    Given user launches application

    When user enters valid username

    And user enters valid password

    And user clicks login button

    Then user should navigate to inventory page