from utils.browser_manager import BrowserManager
from utils.logger import get_logger
from utils.screenshot import capture_screenshot

logger = get_logger()


def before_scenario(context, scenario):

    logger.info(
        f"Starting Scenario : {scenario.name}"
    )

    (
        context.playwright,
        context.browser,
        context.page
    ) = BrowserManager.launch_browser()


def after_scenario(context, scenario):

    if scenario.status == "failed":

        capture_screenshot(
            context.page
        )

    context.browser.close()

    context.playwright.stop()