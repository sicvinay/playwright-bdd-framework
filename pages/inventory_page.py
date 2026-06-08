from utils.logger import get_logger

logger = get_logger()


class InventoryPage:

    def __init__(self, page):

        self.page = page

    def is_inventory_page_displayed(self):

        logger.info(
            "Validating inventory page"
        )

        return "inventory" in self.page.url