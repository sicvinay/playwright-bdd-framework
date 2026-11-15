from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from utils.logger import get_logger

logger = get_logger()


class InventoryPage:
    def __init__(self, page):
        self.page = page

    def is_inventory_page_displayed(self):
        try:
            self.page.wait_for_url("**/inventory.html", timeout=15000)
            # Check the actual inventory page content rather than a cosmetic title.
            self.page.locator(".inventory_list").wait_for(state="visible", timeout=15000)
            logger.info("Inventory page validated at %s", self.page.url)
            return True
        except PlaywrightTimeoutError:
            logger.error("Inventory page not ready; URL: %s", self.page.url)
            return False
