from config.config import (
    BASE_URL,
    PAGE_LOAD_TIMEOUT_MS,
    DEFAULT_TIMEOUT_MS
)

from locators.login_locators import LoginLocators
from utils.logger import get_logger
from utils.wait_utils import wait_until


logger = get_logger()


class LoginPage:

    def __init__(self, page):

        self.page = page


    def open_application(self):

        logger.info(
            f"BASE_URL loaded = {BASE_URL}"
        )

        if not BASE_URL:

            raise ValueError(
                "BASE_URL is not configured"
            )

        self.page.goto(
            BASE_URL,
            wait_until="domcontentloaded",
            timeout=PAGE_LOAD_TIMEOUT_MS
        )

        self.page.wait_for_selector(
            LoginLocators.USERNAME,
            state="visible",
            timeout=DEFAULT_TIMEOUT_MS
        )

        logger.info(
            "Application launched successfully"
        )


    def enter_username(self, username):

        logger.info(
            f"Entering username: {username}"
        )

        self.page.fill(
            LoginLocators.USERNAME,
            username
        )


    def enter_password(self, password):

        logger.info(
            "Entering password"
        )

        self.page.fill(
            LoginLocators.PASSWORD,
            password
        )


    def click_login(self):

        logger.info(
            "Clicking login button"
        )

        self.page.click(
            LoginLocators.LOGIN_BUTTON
        )


    def get_error_message(self):

        logger.info(
            "Waiting for login error message"
        )

        error_element = self.page.locator(
            LoginLocators.ERROR_MESSAGE
        )

        wait_until(
            condition=lambda: error_element.is_visible(),
            error_message=(
                "Login error message was not displayed "
                "within the configured timeout"
            )
        )

        error_message = error_element.inner_text()

        logger.info(
            f"Login error message displayed: {error_message}"
        )

        return error_message