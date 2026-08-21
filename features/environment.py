from config.config import (
    DEFAULT_TIMEOUT_MS,
    PAGE_LOAD_TIMEOUT_MS
)

from utils.browser_manager import BrowserManager
from utils.logger import get_logger
from utils.screenshot import capture_screenshot


logger = get_logger()


def before_scenario(context, scenario):

    logger.info(
        f"Starting Scenario: {scenario.name}"
    )

    (
        context.playwright,
        context.browser,
        context.page
    ) = BrowserManager.launch_browser()

    # Set default timeout for Playwright actions
    context.page.set_default_timeout(
        DEFAULT_TIMEOUT_MS
    )

    # Set default timeout for page navigation
    context.page.set_default_navigation_timeout(
        PAGE_LOAD_TIMEOUT_MS
    )

    logger.info(
        f"Default timeout configured: "
        f"{DEFAULT_TIMEOUT_MS} ms"
    )

    logger.info(
        f"Page load timeout configured: "
        f"{PAGE_LOAD_TIMEOUT_MS} ms"
    )

    logger.info(
        "Browser launched successfully"
    )


def after_scenario(context, scenario):

    try:

        if scenario.status.name == "failed":

            logger.error(
                f"Scenario failed: {scenario.name}"
            )

            logger.info(
                "Capturing failure screenshot"
            )

            capture_screenshot(
                context.page
            )

        else:

            logger.info(
                f"Scenario completed successfully: "
                f"{scenario.name}"
            )

    finally:

        logger.info(
            "Closing browser"
        )

        context.browser.close()

        logger.info(
            "Stopping Playwright"
        )

        context.playwright.stop()