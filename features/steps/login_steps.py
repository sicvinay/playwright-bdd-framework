from behave import *

from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage


@given("user launches application")
def step_launch_application(context):

    context.login_page = LoginPage(
        context.page
    )

    context.login_page.open_application()


@when("user enters valid username")
def step_enter_username(context):

    context.login_page.enter_username()


@when("user enters valid password")
def step_enter_password(context):

    context.login_page.enter_password()


@when("user clicks login button")
def step_click_login(context):

    context.login_page.click_login()


@then("user should navigate to inventory page")
def step_verify_inventory(context):

    inventory_page = InventoryPage(
        context.page
    )

    assert inventory_page.is_inventory_page_displayed()