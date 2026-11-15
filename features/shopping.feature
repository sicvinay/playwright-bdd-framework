@shopping
Feature: Shopping journey
  As a SauceDemo customer
  I want to browse and purchase products

  Background:
    Given a standard customer is logged in

  @smoke @inventory
  Scenario: Inventory is displayed after login
    Then the inventory should contain 6 products

  @inventory
  Scenario: Sort products by price from low to high
    When the customer sorts products by price low to high
    Then inventory prices should be in ascending order

  @cart
  Scenario: Add and remove an item from cart
    When the customer adds "Sauce Labs Backpack" to the cart
    Then the cart should contain "Sauce Labs Backpack"
    When the customer removes "Sauce Labs Backpack" from the cart
    Then the cart should not contain "Sauce Labs Backpack"

  @smoke @checkout
  Scenario: Complete checkout successfully
    When the customer adds "Sauce Labs Backpack" to the cart
    And the customer starts checkout
    And the customer enters checkout details "Test" "Customer" "560001"
    And the customer finishes checkout
    Then the order confirmation should be "Thank you for your order!"

  @negative @checkout
  Scenario: Checkout requires first name
    When the customer adds "Sauce Labs Backpack" to the cart
    And the customer starts checkout
    And the customer submits checkout with an empty first name
    Then checkout should display "Error: First Name is required"
