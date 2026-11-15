class CheckoutPage:
    def __init__(self, page):
        self.page = page

    def enter_customer_information(self, first_name, last_name, postal_code):
        self.page.locator("[data-test='firstName']").fill(first_name)
        self.page.locator("[data-test='lastName']").fill(last_name)
        self.page.locator("[data-test='postalCode']").fill(postal_code)
        self.page.locator("[data-test='continue']").click()

    def finish_order(self):
        self.page.locator("[data-test='finish']").click()

    def confirmation_message(self):
        return self.page.locator("[data-test='complete-header']").inner_text()

    def error_message(self):
        return self.page.locator("[data-test='error']").inner_text()
