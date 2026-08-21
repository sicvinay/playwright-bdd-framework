from locators.inventory_locators import InventoryLocators
from utils.logger import get_logger


logger = get_logger()


class InventoryPage:

    def __init__(self, page):

        self.page = page


    def is_inventory_page_displayed(self):

        logger.info(
            "Validating inventory page"
        )

        current_url = self.page.url

        is_inventory_url = (
            "inventory.html" in current_url
        )

        is_inventory_title_visible = (
            self.page.locator(
                InventoryLocators.PAGE_TITLE
            ).is_visible()
        )

        if is_inventory_url and is_inventory_title_visible:

            logger.info(
                "Inventory page validated successfully"
            )

            return True

        logger.error(
            f"Inventory page validation failed. "
            f"Current URL: {current_url}"
        )

        return False