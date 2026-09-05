import os

from config.config import (
    DEFAULT_TIMEOUT_MS,
    PAGE_LOAD_TIMEOUT_MS
)

from utils.browser_manager import BrowserManager
from utils.logger import get_logger
from utils.screenshot import capture_screenshot
from utils.allure_utils import (
    attach_screenshot,
    attach_video,
    attach_trace
)


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

        scenario_name = (
            scenario.name
            .replace(" ", "_")
            .replace("/", "_")
            .replace("\\", "_")
        )

        logger.info(
            f"Scenario status: {scenario.status.name}"
        )

        # -------------------------------------------------
        # 1. Capture screenshot
        # -------------------------------------------------

        logger.info(
            "Capturing scenario screenshot"
        )

        screenshot_path = capture_screenshot(
            context.page,
            scenario.name
        )

        if screenshot_path and os.path.exists(
            screenshot_path
        ):

            attach_screenshot(
                screenshot_path,
                name=f"{scenario_name}_screenshot"
            )

        # -------------------------------------------------
        # 2. Stop Playwright trace
        # -------------------------------------------------

        trace_path = (
            f"reports/traces/{scenario_name}.zip"
        )

        logger.info(
            "Stopping Playwright trace"
        )

        context.browser_context.tracing.stop(
            path=trace_path
        )

        if os.path.exists(trace_path):

            attach_trace(
                trace_path,
                name=f"{scenario_name}_trace"
            )

        # -------------------------------------------------
        # 3. Get video path
        # -------------------------------------------------

        video_path = None

        if context.page.video:

            logger.info(
                "Finalizing Playwright video"
            )

            video_path = context.page.video.path()

        # -------------------------------------------------
        # 4. Close browser context
        # -------------------------------------------------

        logger.info(
            "Closing browser context"
        )

        context.browser_context.close()

        # -------------------------------------------------
        # 5. Attach video after context closes
        # -------------------------------------------------

        if video_path and os.path.exists(video_path):

            attach_video(
                video_path,
                name=f"{scenario_name}_video"
            )

        # -------------------------------------------------
        # 6. Log scenario result
        # -------------------------------------------------

        if scenario.status.name == "failed":

            logger.error(
                f"Scenario failed: {scenario.name}"
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

        if context.browser:

            context.browser.close()

        logger.info(
            "Stopping Playwright"
        )

        if context.playwright:

            context.playwright.stop()