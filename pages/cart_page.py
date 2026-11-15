class CartPage:
    def __init__(self, page):
        self.page = page

    def open_cart(self):
        self.page.locator("[data-test='shopping-cart-link']").click()

    def item_names(self):
        return self.page.locator("[data-test='inventory-item-name']").all_inner_texts()

    def remove_item(self, item_name):
        item = self.page.locator(".cart_item").filter(
            has=self.page.get_by_text(item_name, exact=True)
        )
        item.get_by_role("button", name="Remove").click()

    def checkout(self):
        self.page.locator("[data-test='checkout']").click()
