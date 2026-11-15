from behave import given, when, then

from pages.login_page import LoginPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage


@given("a standard customer is logged in")
def login_customer(context):
    login = LoginPage(context.page)
    login.open_application()
    login.enter_username("standard_user")
    login.enter_password("secret_sauce")
    login.click_login()
    context.page.wait_for_url("**/inventory.html")


@then("the inventory should contain {count:d} products")
def verify_inventory_count(context, count):
    context.page.locator(".inventory_list").wait_for(state="visible", timeout=15000)
    actual = context.page.locator(".inventory_item").count()
    assert actual == count, f"Expected {count} inventory items, found {actual}; URL={context.page.url}"


@when("the customer sorts products by price low to high")
def sort_prices(context):
    context.page.locator("[data-test='product-sort-container']").select_option("lohi")


@then("inventory prices should be in ascending order")
def verify_price_sort(context):
    prices = [
        float(text.replace("$", ""))
        for text in context.page.locator("[data-test='inventory-item-price']").all_inner_texts()
    ]
    assert prices == sorted(prices), f"Unexpected price order: {prices}"


@when('the customer adds "{item_name}" to the cart')
def add_to_cart(context, item_name):
    product = context.page.locator("[data-test='inventory-item']").filter(
        has=context.page.get_by_text(item_name, exact=True)
    )
    product.get_by_role("button", name="Add to cart").click()


@then('the cart should contain "{item_name}"')
def verify_cart_item(context, item_name):
    cart = CartPage(context.page)
    cart.open_cart()
    assert item_name in cart.item_names()


@when('the customer removes "{item_name}" from the cart')
def remove_from_cart(context, item_name):
    CartPage(context.page).remove_item(item_name)


@then('the cart should not contain "{item_name}"')
def verify_item_removed(context, item_name):
    assert item_name not in CartPage(context.page).item_names()


@when("the customer starts checkout")
def start_checkout(context):
    cart = CartPage(context.page)
    cart.open_cart()
    cart.checkout()


@when('the customer enters checkout details "{first}" "{last}" "{postal}"')
def fill_checkout(context, first, last, postal):
    CheckoutPage(context.page).enter_customer_information(first, last, postal)


@when("the customer finishes checkout")
def finish_checkout(context):
    CheckoutPage(context.page).finish_order()


@then('the order confirmation should be "{message}"')
def verify_confirmation(context, message):
    assert CheckoutPage(context.page).confirmation_message() == message


@then('checkout should display "{message}"')
def verify_checkout_error(context, message):
    assert CheckoutPage(context.page).error_message() == message


@when("the customer submits checkout with an empty first name")
def submit_without_first_name(context):
    CheckoutPage(context.page).enter_customer_information("", "Customer", "560001")
