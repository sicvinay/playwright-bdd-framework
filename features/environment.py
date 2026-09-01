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
        context.browser_context,
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

        logger.info(
            f"Scenario status: {scenario.status.name}"
        )

        # Capture screenshot for every scenario
        logger.info(
            "Capturing scenario screenshot"
        )

        capture_screenshot(
            context.page,
            scenario.name
        )

        # Stop Playwright trace
        logger.info(
            "Stopping Playwright trace"
        )

        trace_name = (
            scenario.name
            .replace(" ", "_")
            .replace("/", "_")
            .replace("\\", "_")
        )

        context.browser_context.tracing.stop(
            path=f"reports/traces/{trace_name}.zip"
        )

        logger.info(
            f"Trace saved: {trace_name}.zip"
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