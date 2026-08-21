from behave import given, when, then

from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage


@given("user launches the application")
def step_launch_application(context):

    context.login_page = LoginPage(
        context.page
    )

    context.login_page.open_application()


@when(
    'user logs in with username "{username}" and password "{password}"'
)
def step_login_with_credentials(
    context,
    username,
    password
):

    context.login_page.enter_username(
        username
    )

    context.login_page.enter_password(
        password
    )

    context.login_page.click_login()


@when(
    'user logs in with empty username and password "{password}"'
)
def step_login_with_empty_username(
    context,
    password
):

    context.login_page.enter_username(
        ""
    )

    context.login_page.enter_password(
        password
    )

    context.login_page.click_login()


@when(
    'user logs in with username "{username}" and empty password'
)
def step_login_with_empty_password(
    context,
    username
):

    context.login_page.enter_username(
        username
    )

    context.login_page.enter_password(
        ""
    )

    context.login_page.click_login()


@then(
    "the user should be redirected to the inventory page"
)
def step_verify_inventory_page(context):

    inventory_page = InventoryPage(
        context.page
    )

    assert inventory_page.is_inventory_page_displayed(), (
        "User was not redirected to the inventory page"
    )


@then(
    'the user should see the error message "{expected_error_message}"'
)
def step_verify_error_message(
    context,
    expected_error_message
):

    actual_error_message = (
        context.login_page.get_error_message()
    )

    assert actual_error_message == expected_error_message, (
        f"Expected error message: "
        f"'{expected_error_message}', "
        f"but got: "
        f"'{actual_error_message}'"
    )