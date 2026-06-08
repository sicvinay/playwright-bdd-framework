from config.config import (
    BASE_URL,
    APP_USERNAME,
    APP_PASSWORD
)

from locators.login_locators import LoginLocators
from utils.logger import get_logger

logger = get_logger()


class LoginPage:

    def __init__(self, page):
        self.page = page

    def open_application(self):
        logger.info(
            f"BASE_URL loaded = {BASE_URL}"
        )

        if not BASE_URL:
            raise ValueError("BASE_URL is not configured")

        logger.info(
            "Application credentials loaded successfully"
        )

        self.page.goto(
            BASE_URL,
            wait_until="domcontentloaded",
            timeout=60000
        )

        self.page.wait_for_selector(
            LoginLocators.USERNAME,
            timeout=60000
        )

    def enter_username(self):

        logger.info(
            "Entering username"
        )

        self.page.fill(
            LoginLocators.USERNAME,
            APP_USERNAME
        )

    def enter_password(self):

        logger.info(
            "Entering password"
        )

        self.page.fill(
            LoginLocators.PASSWORD,
            APP_PASSWORD
        )

    def click_login(self):

        logger.info(
            "Clicking login button"
        )

        self.page.click(
            LoginLocators.LOGIN_BUTTON
        )
